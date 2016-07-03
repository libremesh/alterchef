try:
    import ipdb as pdb
except ImportError:
    import pdb

from django import template

register = template.Library()


class PdbNode(template.Node):
    def render(self, context):
        # Access vars at the prompt for an easy reference to
        # variables in the context
        vars = []
        for dict in context.dicts:
            for k, v in dict.items():
                vars.append(k)
                locals()[k] = v
        pdb.set_trace()
        # You may access all context variables directly (they are stored in locals())
        return ''


@register.tag("pdb_debug")
def pdbdebug_tag(parser, token):
    """Tag that inspects template context.

    Usage:
    {% pdb_debug %}

    You can then access your context variables directly at the prompt.

    The vars variable additonally has a reference list of keys
    in the context.
    """
    return PdbNode()
