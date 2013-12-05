# -*- coding: utf-8 -*-
import logging
import logging.config

LOGGING_CONFIG = {
	'version': 1,
	'disable_existing_loggers': False,
	'formatters': {
		'verbose': {
			'format': '%(asctime)s %(levelname)s %(module)s - %(message)s'
		},
		'simple': {
			'format': '%(levelname)s %(message)s'
		},
	},
	'handlers': {
		'file': {
			'level': 'INFO',
			'class': 'logging.handlers.RotatingFileHandler',
			'filename': 'monitor.log',
			'maxBytes': 1024,
			'backupCount': 3,
			'formatter' : 'verbose'
		},
		'console': {
			'level': 'DEBUG',
			'class': 'logging.StreamHandler',
			'formatter' : 'simple'
		},
	},
	'loggers': {
		'root': {
			'handlers': ['console', 'file'],
			'level': 'DEBUG',
			'propagate': True,
		},
	}
}

logging.config.dictConfig(LOGGING_CONFIG) 
log = logging.getLogger('root')

