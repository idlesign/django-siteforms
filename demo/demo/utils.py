from django.shortcuts import render


def render_themed(request, view_type, context):
    theme = context['theme']
    context.update({
        'tpl_head': '_head_%s.html' % theme,
        'tpl_realm': '%s_%s.html' % (view_type, theme)
    })
    return render(request, '%s.html' % view_type, context)
