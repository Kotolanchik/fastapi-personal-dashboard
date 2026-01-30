{{- define "personal-dashboard.name" -}}
personal-dashboard
{{- end -}}

{{- define "personal-dashboard.fullname" -}}
{{ include "personal-dashboard.name" . }}
{{- end -}}
