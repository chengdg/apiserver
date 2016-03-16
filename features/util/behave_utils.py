# -*- coding: utf-8 -*-


def get_context_attrs(context, *args, **kwargs):
	if context._stack:
		raw_context_kvs = context._stack[0]
		context_kvs = {}
		for k, v in raw_context_kvs.items():
			if isinstance(v, (basestring, int, float, list, dict, bool)):
				context_kvs[k] = v
		return context_kvs
	else:
		return {}


def set_context_attrs(context, context_kvs):
	for k, v in context_kvs.items():
		setattr(context, k, v)
