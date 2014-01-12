# -*- coding: utf-8 -*-
import os
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
		'trader': {
			'format': '%(message)s'
		},
	},
	'handlers': {
		'file': {
			'level': 'INFO',
			'class': 'logging.handlers.RotatingFileHandler',
			'filename': os.path.join(os.path.dirname(__file__), '../logs/main.log'),
			'maxBytes': 1048576,
			'backupCount': 3,
			'formatter' : 'verbose'
		},
		'trader': {
			'level': 'INFO',
			'class': 'logging.handlers.RotatingFileHandler',
			'filename': os.path.join(os.path.dirname(__file__), '../logs/trader.csv'),
			'maxBytes': 10485760,
			'backupCount': 3,
			'formatter' : 'trader'
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
		'trader': {
			'handlers': ['trader'],
			'level': 'INFO',
			'propagate': True,
		},
	}
}

logging.config.dictConfig(LOGGING_CONFIG) 
log = logging.getLogger('root')
tradeLogger = logging.getLogger('trader')


