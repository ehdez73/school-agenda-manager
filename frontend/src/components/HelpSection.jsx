import { useEffect, useMemo, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';

import api from '../lib/api';
import { t } from '../i18n';
import SectionLayout from './SectionLayout';
import './HelpSection.css';

const HELP_REFRESH_INTERVAL_MS = 15000;

function cleanHeadingTitle(value) {
  return (value || '')
    .replace(/\[(.*?)\]\(.*?\)/g, '$1')
    .replace(/`/g, '')
    .trim();
}

function slugify(value) {
  const slug = (value || '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-');

  return slug || 'section';
}

function extractHeadings(markdown) {
  if (!markdown) return [];

  const lines = markdown.replace(/\r\n/g, '\n').split('\n');
  const headings = [];
  let insideFence = false;

  for (const line of lines) {
    if (line.trimStart().startsWith('```')) {
      insideFence = !insideFence;
      continue;
    }

    if (insideFence) continue;

    const match = line.match(/^(#{1,4})\s+(.+)$/);
    if (!match) continue;

    const level = match[1].length;
    const rawTitle = cleanHeadingTitle(match[2]);
    if (!rawTitle) continue;

    const id = `section-${headings.length + 1}`;
    const aliases = [];
    const titleSlug = slugify(rawTitle);
    if (titleSlug && titleSlug !== id) {
      aliases.push(titleSlug);
    }

    headings.push({ id, title: rawTitle, level, aliases });
  }

  return headings;
}

function buildTocGroups(headings) {
  if (!headings.length) return [];

  const groups = [];
  let currentGroup = null;

  for (const heading of headings) {
    if (heading.level <= 2 || !currentGroup) {
      currentGroup = { ...heading, children: [] };
      groups.push(currentGroup);
      continue;
    }

    currentGroup.children.push(heading);
  }

  return groups;
}

function flattenNodeText(children) {
  if (children === null || children === undefined || typeof children === 'boolean') return '';
  if (typeof children === 'string' || typeof children === 'number') return String(children);
  if (Array.isArray(children)) {
    return children.map(flattenNodeText).join('');
  }
  if (typeof children === 'object' && children.props) {
    return flattenNodeText(children.props.children);
  }
  return '';
}

function resolveDocLanguage(locale) {
  return locale === 'es' ? 'es' : 'en';
}

function canUseNativeScrollTo() {
  if (typeof navigator !== 'undefined' && /jsdom/i.test(navigator.userAgent || '')) {
    return false;
  }
  return typeof window.scrollTo === 'function' && /\[native code\]/.test(String(window.scrollTo));
}

function getAlternateDocLanguage(locale) {
  return resolveDocLanguage(locale) === 'es' ? 'en' : 'es';
}

function isExternalAsset(src) {
  return /^(?:[a-z][a-z0-9+.-]*:|\/\/)/i.test(src) || src.startsWith('data:') || src.startsWith('#');
}

function resolveHelpImageSrc(src) {
  const cleanedSrc = (src || '').trim();
  if (!cleanedSrc || isExternalAsset(cleanedSrc)) return cleanedSrc;

  const normalizedSrc = cleanedSrc
    .replace(/^\.\//, '')
    .replace(/^\//, '')
    .replace(/^assets\//, '')
    .replace(/^docs\//, '');

  const apiBase = api.API_BASE || '/api';
  return `${apiBase}/api/docs/assets/${normalizedSrc}`;
}

function markdownContainsHashTarget(markdown, hashTargetId) {
  if (!markdown || !hashTargetId) return false;

  const targetSlug = slugify(hashTargetId);
  if (!targetSlug) return false;

  return extractHeadings(markdown).some(heading => {
    return heading.id === hashTargetId || (heading.aliases || []).includes(targetSlug);
  });
}

function mapHashTargetByHeadingOrder(hashTargetId, sourceMarkdown, targetMarkdown) {
  if (!hashTargetId || !sourceMarkdown || !targetMarkdown) return null;

  const sourceHeadings = extractHeadings(sourceMarkdown);
  const targetHeadings = extractHeadings(targetMarkdown);
  if (!sourceHeadings.length || !targetHeadings.length) return null;

  const targetSlug = slugify(hashTargetId);
  const sourceIndex = sourceHeadings.findIndex(heading => (
    heading.id === hashTargetId ||
    slugify(heading.id) === targetSlug ||
    slugify(heading.title) === targetSlug
  ));

  if (sourceIndex < 0 || sourceIndex >= targetHeadings.length) return null;
  return targetHeadings[sourceIndex]?.id || null;
}

function resolveCanonicalHashId(markdown, hashTargetId) {
  if (!markdown || !hashTargetId) return null;

  const targetSlug = slugify(hashTargetId);
  if (!targetSlug) return null;

  const headings = extractHeadings(markdown);
  const headingIndex = headings.findIndex(heading => (
    heading.id === hashTargetId || (heading.aliases || []).includes(targetSlug)
  ));

  if (headingIndex < 0) return null;
  return headings[headingIndex]?.id || null;
}

function getHashTargetId() {
  const rawHash = window.location.hash || '';
  if (!rawHash.startsWith('#') || rawHash.length <= 1) return null;
  return decodeURIComponent(rawHash.slice(1));
}

function resolveHashTargetElement(targetId) {
  if (!targetId) return null;

  // Exact id match first.
  let target = document.getElementById(targetId);
  if (target) return target;

  // Fallback: normalize hash text to the same slug format used for headings.
  const normalizedId = slugify(targetId);
  if (!normalizedId) return null;

  target = document.getElementById(normalizedId);
  if (target) return target;

  // Legacy title slug fallback stored on rendered headings.
  const aliasSelector = `[data-help-hash-aliases~="${normalizedId}"]`;
  target = document.querySelector(aliasSelector);
  if (target) return target;

  // Last fallback: case-insensitive id scan.
  const lower = normalizedId.toLowerCase();
  target = Array.from(document.querySelectorAll('[id]')).find(
    node => (node.id || '').toLowerCase() === lower
  ) || null;

  if (target) return target;

  // Final fallback: match by visible heading text, which is stable even if ids are auto-suffixed.
  const normalizedTargetText = normalizedId.replace(/-/g, ' ');
  return Array.from(document.querySelectorAll('.help-section__markdown h1, .help-section__markdown h2, .help-section__markdown h3, .help-section__markdown h4')).find(
    node => slugify(node.textContent || '') === normalizedId || slugify(node.textContent || '').includes(normalizedTargetText)
  ) || null;
}

function scrollToHashTarget({ behavior = 'auto' } = {}) {
  const targetId = getHashTargetId();
  if (!targetId) return false;

  const target = resolveHashTargetElement(targetId);
  if (!target) return false;

  // Keep headings visible below the sticky app navigation.
  const nav = document.querySelector('.app__nav');
  const navOffset = nav instanceof HTMLElement ? nav.offsetHeight : 0;

  const targetTop = Math.max(
    0,
    Math.round(target.getBoundingClientRect().top + window.scrollY - navOffset - 12)
  );

  try {
    if (canUseNativeScrollTo()) {
      window.scrollTo({ top: targetTop, behavior });
    } else {
      throw new Error('scrollTo unavailable');
    }
  } catch {
    const root = document.documentElement || document.body;
    if (root) {
      root.scrollTop = targetTop;
    }
    if (document.body) {
      document.body.scrollTop = targetTop;
    }
  }

  return true;
}

function scheduleHashScroll({ behavior = 'auto' } = {}) {
  let attempts = 0;
  const maxAttempts = 24;

  const tryScroll = () => {
    const currentBehavior = attempts === 0 ? behavior : 'auto';
    if (scrollToHashTarget({ behavior: currentBehavior })) return;
    if (attempts >= maxAttempts) return;
    attempts += 1;
    window.setTimeout(tryScroll, 90);
  };

  window.requestAnimationFrame(() => {
    window.requestAnimationFrame(tryScroll);
  });
}

export default function HelpSection({ locale = 'en' }) {
  const [markdown, setMarkdown] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedGroupIds, setExpandedGroupIds] = useState([]);
  const [hashToken, setHashToken] = useState(() => window.location.hash || '');

  useEffect(() => {
    let isMounted = true;
    let intervalId = null;

    const fetchHelp = async ({ silent = false } = {}) => {
      const targetHashId = getHashTargetId();
      const currentDocLocale = resolveDocLanguage(locale);
      const alternateDocLocale = getAlternateDocLanguage(locale);

      const loadDoc = async docLocale => {
        const response = await api.get(`/api/docs/${docLocale}`, { responseType: 'text', cacheBust: true });
        if (!isMounted) return null;
        return response || '';
      };

      if (!silent) {
        setLoading(true);
        setError(null);
      }
      try {
        let response = await loadDoc(currentDocLocale);

        const nextMarkdown = response || '';
        if (targetHashId && nextMarkdown) {
          const canonicalHashId = resolveCanonicalHashId(nextMarkdown, targetHashId);

          if (canonicalHashId) {
            if (window.location.hash !== `#${canonicalHashId}`) {
              window.history.replaceState(null, '', `#${canonicalHashId}`);
              setHashToken(`#${canonicalHashId}`);
            }
          } else {
            const alternateResponse = await loadDoc(alternateDocLocale);
            const fallbackCanonicalHashId = resolveCanonicalHashId(alternateResponse, targetHashId);

            if (fallbackCanonicalHashId) {
              const translatedHashId = mapHashTargetByHeadingOrder(targetHashId, alternateResponse, nextMarkdown);
              const nextHashId = translatedHashId || fallbackCanonicalHashId;
              if (window.location.hash !== `#${nextHashId}`) {
                window.history.replaceState(null, '', `#${nextHashId}`);
                setHashToken(`#${nextHashId}`);
              }
            } else if (window.location.hash) {
              window.history.replaceState(null, '', `${window.location.pathname}${window.location.search}`);
              setHashToken('');
            }
          }
        }

        if (!isMounted) return;
        setMarkdown(nextMarkdown);
        if (silent) {
          setError(null);
        }
      } catch (err) {
        if (!isMounted) return;
        if (!silent) {
          setMarkdown('');
        }
        setError(err?.message || t('help.load_error'));
      } finally {
        if (!isMounted || silent) return;
        setLoading(false);
      }
    };

    fetchHelp();
    intervalId = window.setInterval(() => {
      fetchHelp({ silent: true });
    }, HELP_REFRESH_INTERVAL_MS);

    return () => {
      isMounted = false;
      if (intervalId) {
        window.clearInterval(intervalId);
      }
    };
  }, [locale, hashToken]);

  useEffect(() => {
    if (!markdown) return;

    let attempts = 0;
    const maxAttempts = 40;
    let timerId = null;

    const tryScroll = () => {
      if (scrollToHashTarget()) return;
      if (attempts >= maxAttempts) return;
      attempts += 1;
      timerId = window.setTimeout(tryScroll, 90);
    };

    tryScroll();

    return () => {
      if (timerId) window.clearTimeout(timerId);
    };
  }, [markdown, hashToken]);

  useEffect(() => {
    const onHashChange = () => {
      setHashToken(window.location.hash || '');
      // Let the browser update location first, then align with sticky nav offset.
      window.setTimeout(() => {
        scrollToHashTarget({ behavior: 'smooth' });
      }, 0);
    };

    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  const sectionState = loading ? 'loading' : error ? 'error' : markdown ? 'ready' : 'empty';
  const headings = useMemo(() => extractHeadings(markdown), [markdown]);
  const tocHeadings = useMemo(() => headings.filter(heading => heading.level <= 3), [headings]);
  const tocGroups = useMemo(() => buildTocGroups(tocHeadings), [tocHeadings]);
  const tocGroupSignature = useMemo(() => tocGroups.map(group => group.id).join('|'), [tocGroups]);

  useEffect(() => {
    setExpandedGroupIds(tocGroups.filter(group => group.children.length > 0).map(group => group.id));
  }, [tocGroupSignature]);

  const toggleGroup = groupId => {
    setExpandedGroupIds(prev => (
      prev.includes(groupId)
        ? prev.filter(id => id !== groupId)
        : [...prev, groupId]
    ));
  };

  const handleTocLinkClick = (event, targetId) => {
    if (
      event.defaultPrevented ||
      event.button !== 0 ||
      event.metaKey ||
      event.ctrlKey ||
      event.shiftKey ||
      event.altKey
    ) {
      return;
    }

    event.preventDefault();

    const nextHash = `#${targetId}`;
    if (window.location.hash !== nextHash) {
      window.location.hash = nextHash.slice(1);
    } else {
      window.history.replaceState(null, '', nextHash);
    }

    setHashToken(nextHash);
    scheduleHashScroll({ behavior: 'smooth' });
  };

  const headingUsageBySlug = new Map();
  const headingRenderer = level => ({ children, ...props }) => {
    const plainText = cleanHeadingTitle(flattenNodeText(children));
    const normalizedSlug = slugify(plainText);
    const matchingHeadings = headings.filter(heading => (
      slugify(heading.title) === normalizedSlug || (heading.aliases || []).includes(normalizedSlug)
    ));
    const occurrenceIndex = headingUsageBySlug.get(normalizedSlug) || 0;
    headingUsageBySlug.set(normalizedSlug, occurrenceIndex + 1);
    const headingInfo = matchingHeadings[occurrenceIndex] || headings.find(heading => cleanHeadingTitle(heading.title) === plainText);
    const id = headingInfo?.id || `section-${headings.length + 1}`;
    const aliases = headingInfo?.aliases || [];
    const Tag = `h${level}`;

    return (
      <Tag {...props} id={id} data-help-hash-aliases={aliases.join(' ')}>
        {children}
      </Tag>
    );
  };

  return (
    <SectionLayout
      title={t('help.title')}
      state={sectionState}
      errorMsg={error || t('help.load_error')}
      emptyMsg={t('help.empty')}
      className="help-section"
      data-testid="help-section"
    >
      <div className="help-section__layout">
        {tocGroups.length > 0 && (
          <aside className="help-section__toc" aria-label={t('help.toc_title')}>
            <h3 className="help-section__toc-title">{t('help.toc_title')}</h3>
            <nav>
              <ul className="help-section__toc-list">
                {tocGroups.map(group => {
                  const hasChildren = group.children.length > 0;
                  const isExpanded = expandedGroupIds.includes(group.id);

                  return (
                    <li key={group.id} className={`help-section__toc-item help-section__toc-item--level-${group.level}`}>
                      <div className="help-section__toc-row">
                        {hasChildren ? (
                          <button
                            type="button"
                            className="help-section__toc-toggle"
                            onClick={() => toggleGroup(group.id)}
                            aria-expanded={isExpanded}
                            aria-label={isExpanded ? t('help.collapse') : t('help.expand')}
                          />
                        ) : (
                          <span className="help-section__toc-spacer" aria-hidden="true" />
                        )}
                        <a
                          href={`#${group.id}`}
                          className="help-section__toc-link"
                          onClick={event => handleTocLinkClick(event, group.id)}
                        >
                          {group.title}
                        </a>
                      </div>
                      {hasChildren && isExpanded && (
                        <ul className="help-section__toc-sublist">
                          {group.children.map(child => (
                            <li key={child.id} className={`help-section__toc-item help-section__toc-item--level-${child.level}`}>
                              <a
                                href={`#${child.id}`}
                                className="help-section__toc-link"
                                onClick={event => handleTocLinkClick(event, child.id)}
                              >
                                {child.title}
                              </a>
                            </li>
                          ))}
                        </ul>
                      )}
                    </li>
                  );
                })}
              </ul>
            </nav>
          </aside>
        )}
        <div className="help-section__markdown">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            rehypePlugins={[rehypeRaw]}
            components={{
              h1: headingRenderer(1),
              h2: headingRenderer(2),
              h3: headingRenderer(3),
              h4: headingRenderer(4),
              img: ({ src, alt, ...props }) => (
                <img {...props} src={resolveHelpImageSrc(src)} alt={alt || ''} loading="lazy" />
              ),
            }}
          >
            {markdown}
          </ReactMarkdown>
        </div>
      </div>
    </SectionLayout>
  );
}
