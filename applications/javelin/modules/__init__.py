# -*- coding: utf-8 -*-
"""
	Javelin Web2Py Modules
"""

# metadata
__author__ = "Jeremy Jacobson"
__copyright__ = "(c) 2013, Jacobson and Varni, LLC"
__date__ = "7/5/2013"
__email__ = "jjacobson93@gmail.com"

__all__ = ['people']
modules_enabled = list()

for m in __all__:
	modules_enabled.append(__import__('applications.javelin.modules.%s' % m, globals(), locals(), [m]))