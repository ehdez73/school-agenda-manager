import { useEffect, useMemo, useState } from 'react';
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
  return `${apiBase}/docs/assets/${normalizedSrc}`;
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

function scrollToHashTarget({ behavior = 'auto', targetId = null } = {}) {
  const resolvedTargetId = targetId || getHashTargetId();
  if (!resolvedTargetId) return false;

  const target = resolveHashTargetElement(resolvedTargetId);
  if (!target) return false;

  const content = target.closest('.app__content') || document.querySelector('.app__content');
  if (!(content instanceof HTMLElement)) return false;

  const contentRect = content.getBoundingClientRect();
  const targetRect = target.getBoundingClientRect();
  const offset = 12;

  const targetTop = Math.max(
    0,
    Math.round(content.scrollTop + (targetRect.top - contentRect.top) - offset)
  );

  if (typeof content.scrollTo === 'function') {
    content.scrollTo({ top: targetTop, behavior });
  } else {
    content.scrollTop = targetTop;
  }
  return true;
}

function scrollToCurrentHashTarget({ behavior = 'auto' } = {}) {
  const targetId = getHashTargetId();
  if (!targetId) return false;

  return scrollToHashTarget({ behavior, targetId });
}

export default function HelpSection({ locale = 'en' }) {
  const [markdown, setMarkdown] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [hashToken, setHashToken] = useState(() => window.location.hash || '');
  const [activeTocId, setActiveTocId] = useState('');
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    let isMounted = true;
    let intervalId = null;

    const fetchHelp = async ({ silent = false } = {}) => {
      const targetHashId = getHashTargetId();
      const currentDocLocale = resolveDocLanguage(locale);
      const alternateDocLocale = getAlternateDocLanguage(locale);

      const loadDoc = async docLocale => {
        const response = await api.get(`/docs/${docLocale}`, { responseType: 'text', cacheBust: true });
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
        if (!isMounted || silent) {/* don't set loading */}
        else { setLoading(false); }
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
  }, [locale]);

  useEffect(() => {
    if (!markdown) return;

    let attempts = 0;
    const maxAttempts = 40;
    let timerId = null;

    const tryScroll = () => {
      if (scrollToCurrentHashTarget()) return;
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
    if (!markdown) {
      setActiveTocId('');
      return;
    }

    const content = document.querySelector('.app__content');
    if (!(content instanceof HTMLElement)) return;

    const getHeadingNodes = () => {
      return Array.from(
        document.querySelectorAll('.help-section__markdown h1, .help-section__markdown h2, .help-section__markdown h3, .help-section__markdown h4')
      ).filter(node => node.id);
    };

    const updateActiveHeading = () => {
      const headingNodes = getHeadingNodes();
      if (!headingNodes.length) {
        setActiveTocId('');
        return;
      }

      const contentTop = content.getBoundingClientRect().top;
      const activationOffset = 36;
      let candidate = headingNodes[0];

      for (const heading of headingNodes) {
        const relativeTop = heading.getBoundingClientRect().top - contentTop;
        if (relativeTop <= activationOffset) {
          candidate = heading;
          continue;
        }
        break;
      }

      const nextActiveId = candidate?.id || '';
      setActiveTocId(prev => (prev === nextActiveId ? prev : nextActiveId));
    };

    updateActiveHeading();
    content.addEventListener('scroll', updateActiveHeading, { passive: true });
    window.addEventListener('resize', updateActiveHeading);

    return () => {
      content.removeEventListener('scroll', updateActiveHeading);
      window.removeEventListener('resize', updateActiveHeading);
    };
  }, [markdown, hashToken]);

  useEffect(() => {
    const onHashChange = () => {
      setHashToken(window.location.hash || '');
    };

    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  const handleDownload = () => {
    if (!markdown.trim()) {
      setError(t('help.no_content_download'));
      return;
    }
    try {
      setDownloading(true);
      const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      const date = new Date().toISOString().split('T')[0];
      const filename = (t('help.md_filename') || 'help-{date}').replace('{date}', date) + '.md';
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError((t('help.md_error') || 'Error downloading markdown') + ': ' + err.message);
    } finally {
      setDownloading(false);
    }
  };

  const handlePrint = () => {
    if (!markdown.trim()) {
      setError(t('help.no_content_print'));
      return;
    }
    window.print();
  };

  const sectionState = loading ? 'loading' : error ? 'error' : markdown ? 'ready' : 'empty';
  const headings = useMemo(() => extractHeadings(markdown), [markdown]);
  const tocHeadings = useMemo(() => headings.filter(heading => heading.level <= 3), [headings]);
  const tocGroups = useMemo(() => buildTocGroups(tocHeadings), [tocHeadings]);

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
    window.history.replaceState(null, '', nextHash);
    setHashToken(nextHash);
    setActiveTocId(targetId);

    // Perform the internal container scroll immediately for direct TOC clicks.
    scrollToHashTarget({ behavior: 'smooth', targetId });
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
      actions={
        <>
          <button
            onClick={handleDownload}
            disabled={downloading || loading || !!error || !markdown.trim()}
            className="btn btn--secondary btn--compact"
            aria-label={t('help.download_md')}
            title={t('help.download_md')}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
          </button>
          <button
            onClick={handlePrint}
            disabled={loading || !!error || !markdown.trim()}
            className="btn btn--secondary btn--compact"
            aria-label={t('help.print_md')}
            title={t('help.print_md')}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="6 9 6 2 18 2 18 9"/>
              <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/>
              <rect x="6" y="14" width="12" height="8"/>
            </svg>
          </button>
        </>
      }
    >
      <div className="help-section__layout">
        {tocGroups.length > 0 && (
          <aside className="help-section__toc" aria-label={t('help.toc_title')}>
            <h3 className="help-section__toc-title">{t('help.toc_title')}</h3>
            <nav>
              <ul className="help-section__toc-list">
                {tocGroups.map(group => {
                  const hasChildren = group.children.length > 0;
                  const hasActiveChild = group.children.some(child => child.id === activeTocId);
                  const isGroupActive = activeTocId === group.id || hasActiveChild;

                  return (
                    <li key={group.id} className={`help-section__toc-item help-section__toc-item--level-${group.level}`}>
                      <div className="help-section__toc-row">
                        <span className="help-section__toc-spacer" aria-hidden="true" />
                        <a
                          href={`#${group.id}`}
                          className={`help-section__toc-link${isGroupActive ? ' help-section__toc-link--active' : ''}${hasActiveChild ? ' help-section__toc-link--active-parent' : ''}`}
                          onClick={event => handleTocLinkClick(event, group.id)}
                        >
                          {group.title}
                        </a>
                      </div>
                      {hasChildren && (
                        <ul className="help-section__toc-sublist">
                          {group.children.map(child => (
                            <li key={child.id} className={`help-section__toc-item help-section__toc-item--level-${child.level}`}>
                              <a
                                href={`#${child.id}`}
                                className={`help-section__toc-link${activeTocId === child.id ? ' help-section__toc-link--active' : ''}`}
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
