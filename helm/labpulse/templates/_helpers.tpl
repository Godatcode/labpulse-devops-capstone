{{- define "labpulse.labels" -}}
app.kubernetes.io/name: labpulse
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}
