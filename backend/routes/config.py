from flask import Blueprint, jsonify, request, abort
import json
import logging
from ..models import Session, Config
from ..schemas import ConfigSchema
from ..translations import t

config_bp = Blueprint('config_bp', __name__)
logger = logging.getLogger(__name__)

DEFAULT_HOUR_NAMES = ["9:00", "10:00", "11:00", "12:00", "13:00"]


@config_bp.route('/config', methods=['GET'])
def get_config():
    logger.info("Fetching config")
    session = Session()
    config = session.query(Config).first()
    if not config:
        
        config = Config(classes_per_day=5, days_per_week=5, hour_names=json.dumps(DEFAULT_HOUR_NAMES))
        session.add(config)
        session.commit()
        logger.info("Created default config during fetch")
    
    cfg = config.to_dict()
    hour_names = cfg.get('hour_names') or []
    if len(hour_names) < cfg['classes_per_day']:
        
        for i in range(len(hour_names), cfg['classes_per_day']):
            hour_names.append(DEFAULT_HOUR_NAMES[i] if i < len(DEFAULT_HOUR_NAMES) else f"Hora {i+1}")
    elif len(hour_names) > cfg['classes_per_day']:
        hour_names = hour_names[:cfg['classes_per_day']]
    cfg['hour_names'] = hour_names

    day_indices = cfg.get('day_indices') or []
    if not day_indices:
        day_indices = list(range(cfg['days_per_week']))
    elif len(day_indices) < cfg['days_per_week']:
        for i in range(len(day_indices), cfg['days_per_week']):
            day_indices.append(i)
    elif len(day_indices) > cfg['days_per_week']:
        day_indices = day_indices[:cfg['days_per_week']]
    cfg['day_indices'] = day_indices

    day_names = [t(f'day.{i}') for i in day_indices]
    cfg['day_names'] = day_names

    result = ConfigSchema(**cfg).model_dump()
    session.close()
    logger.info("Fetched config classes_per_day=%d days_per_week=%d", cfg['classes_per_day'], cfg['days_per_week'])
    return jsonify(result)

@config_bp.route('/config', methods=['POST'])
def set_config():
    data = request.get_json()
    if not data or 'classes_per_day' not in data or 'days_per_week' not in data:
        logger.warning("Config update rejected due to missing required fields")
        abort(400, description=t('errors.missing_classes_per_day'))
    
    days_per_week = data.get('days_per_week')
    if not isinstance(days_per_week, int) or days_per_week < 1 or days_per_week > 7:
        logger.warning("Config update rejected due to invalid days_per_week value=%s", days_per_week)
        abort(400, description=t('errors.invalid_days_per_week'))
    
    day_indices = data.get('day_indices', [])
    if len(set(day_indices)) != len(day_indices):
        logger.warning("Config update rejected due to duplicate day indices")
        abort(400, description=t('errors.duplicate_days'))
    
    session = Session()
    config = session.query(Config).first()
    if not config:
        
        hour_names = data.get('hour_names') or []
        
        if len(hour_names) < data['classes_per_day']:
            for i in range(len(hour_names), data['classes_per_day']):
                hour_names.append(DEFAULT_HOUR_NAMES[i] if i < len(DEFAULT_HOUR_NAMES) else f"Hora {i+1}")
        elif len(hour_names) > data['classes_per_day']:
            hour_names = hour_names[:data['classes_per_day']]

        day_indices = data.get('day_indices') or []
        if not day_indices:
            day_indices = list(range(data['days_per_week']))
        elif len(day_indices) < data['days_per_week']:
            for i in range(len(day_indices), data['days_per_week']):
                day_indices.append(i)
        elif len(day_indices) > data['days_per_week']:
            day_indices = day_indices[:data['days_per_week']]

        disabled = data.get('disabled_restrictions')
        config = Config(
            classes_per_day=data['classes_per_day'],
            days_per_week=data['days_per_week'],
            hour_names=json.dumps(hour_names),
            day_indices=json.dumps(day_indices),
            disabled_restrictions=json.dumps(disabled) if disabled is not None else None,
        )
        session.add(config)
        logger.info("Created config classes_per_day=%d days_per_week=%d", data['classes_per_day'], data['days_per_week'])
    else:
        config.classes_per_day = data['classes_per_day']
        config.days_per_week = data['days_per_week']
        hour_names = data.get('hour_names')
        if hour_names is None:
            
            existing = json.loads(config.hour_names) if config.hour_names else []
            if len(existing) < config.classes_per_day:
                for i in range(len(existing), config.classes_per_day):
                    existing.append(DEFAULT_HOUR_NAMES[i] if i < len(DEFAULT_HOUR_NAMES) else f"Hora {i+1}")
            elif len(existing) > config.classes_per_day:
                existing = existing[:config.classes_per_day]
            config.hour_names = json.dumps(existing)
        else:
            
            if len(hour_names) < config.classes_per_day:
                for i in range(len(hour_names), config.classes_per_day):
                    hour_names.append(DEFAULT_HOUR_NAMES[i] if i < len(DEFAULT_HOUR_NAMES) else f"Hora {i+1}")
            elif len(hour_names) > config.classes_per_day:
                hour_names = hour_names[:config.classes_per_day]
            config.hour_names = json.dumps(hour_names)

        day_indices = data.get('day_indices')
        if day_indices is None:
            existing = json.loads(config.day_indices) if config.day_indices else []
            if not existing:
                existing = list(range(config.days_per_week))
            elif len(existing) < config.days_per_week:
                for i in range(len(existing), config.days_per_week):
                    existing.append(i)
            elif len(existing) > config.days_per_week:
                existing = existing[:config.days_per_week]
            config.day_indices = json.dumps(existing)
        else:
            if not day_indices:
                day_indices = list(range(config.days_per_week))
            elif len(day_indices) < config.days_per_week:
                for i in range(len(day_indices), config.days_per_week):
                    day_indices.append(i)
            elif len(day_indices) > config.days_per_week:
                day_indices = day_indices[:config.days_per_week]
            config.day_indices = json.dumps(day_indices)

        if 'disabled_restrictions' in data:
            config.disabled_restrictions = json.dumps(data['disabled_restrictions'])
        logger.info("Updated existing config classes_per_day=%d days_per_week=%d", config.classes_per_day, config.days_per_week)

    session.commit()
    cfg_dict = config.to_dict()
    day_names = [t(f'day.{i}') for i in cfg_dict.get('day_indices', [])]
    cfg_dict['day_names'] = day_names
    result = ConfigSchema(**cfg_dict).model_dump()
    session.close()
    logger.info("Config update completed")
    return jsonify(result)
