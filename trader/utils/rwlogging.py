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
		'onlymsg': {
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
			'class': 'logging.FileHandler',
			'filename': os.path.join(os.path.dirname(__file__), '../logs/trader.csv'),
			'formatter' : 'onlymsg'
		},
		'balance': {
			'level': 'INFO',
			'class': 'logging.FileHandler',
			'filename': os.path.join(os.path.dirname(__file__), '../logs/balance.csv'),
			'formatter' : 'onlymsg'
		},
		'trades': {
			'level': 'INFO',
			'class': 'logging.FileHandler',
			'filename': os.path.join(os.path.dirname(__file__), '../logs/trades.csv'),
			'formatter' : 'onlymsg'
		},
		'strategy': {
			'level': 'INFO',
			'class': 'logging.FileHandler',
			'filename': os.path.join(os.path.dirname(__file__), '../logs/strategy.csv'),
			'formatter' : 'onlymsg'
		},
		'console': {
			'level': 'DEBUG',
			'class': 'logging.StreamHandler',
			'formatter' : 'onlymsg'
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
		'balance': {
			'handlers': ['trader', 'balance',],
			'level': 'INFO',
			'propagate': True,
		},
		'trades': {
			'handlers': ['trader', 'trades',],
			'level': 'INFO',
			'propagate': True,
		},
		'strategy': {
			'handlers': ['console', 'trader', 'strategy',],
			'level': 'INFO',
			'propagate': True,
		},
	}
}

logging.config.dictConfig(LOGGING_CONFIG) 
log = logging.getLogger('root')
tradeLogger = logging.getLogger('trader')
balLogger = logging.getLogger('balance')
tradesLogger = logging.getLogger('trades')
strategyLogger = logging.getLogger('strategy')


