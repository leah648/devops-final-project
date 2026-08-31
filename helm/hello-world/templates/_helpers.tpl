{{-/*
Common template helpers for hello-world chart
*/-}}
{{- define "hello-world.fullname" -}}
{{- printf "%s-%s" .Release.Name "hello-world" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "hello-world.labels" -}}
app.kubernetes.io/name: {{ include "hello-world.fullname" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}
