# External Android boundary inventory

## activity `com.openai.chatgpt.MainActivity`
- exported: `true`
- enabled: `<default>`
- intent: actions=['android.intent.action.MAIN']; categories=['android.intent.category.LAUNCHER']; data=[]
- intent: actions=['android.intent.action.SEND']; categories=['android.intent.category.DEFAULT']; data=[{'mimeType': 'image/*'}, {'mimeType': 'text/*'}, {'mimeType': 'application/*'}]
- intent: actions=['android.intent.action.SEND_MULTIPLE']; categories=['android.intent.category.DEFAULT']; data=[{'mimeType': 'image/*'}, {'mimeType': 'text/*'}, {'mimeType': 'application/*'}]

## activity `com.openai.chatgpt.ChatGptDeeplinkActivity`
- exported: `true`
- enabled: `<default>`
- intent: actions=['android.intent.action.VIEW']; categories=['android.intent.category.DEFAULT', 'android.intent.category.BROWSABLE']; data=[{'scheme': 'com.openai.chat'}, {'host': 'auth'}, {'pathPattern': '/logout'}, {'pathPattern': '/ext_callback'}, {'pathPattern': '/email_verification'}]
- intent: actions=['android.intent.action.VIEW']; categories=['android.intent.category.DEFAULT', 'android.intent.category.BROWSABLE']; data=[{'scheme': 'com.openai.chat', 'host': 'codex', 'path': '/open'}]
- intent: actions=['android.intent.action.VIEW']; categories=['android.intent.category.DEFAULT', 'android.intent.category.BROWSABLE']; data=[{'scheme': 'https'}, {'scheme': 'http'}, {'host': 'platform.openai.com'}, {'pathPattern': '/auth/logout'}, {'pathPattern': '/auth/ext_callback'}, {'pathPattern': '/auth/email_verification'}]
- intent: actions=['android.intent.action.VIEW']; categories=['android.intent.category.DEFAULT', 'android.intent.category.BROWSABLE']; data=[{'scheme': 'https'}, {'host': 'link.openai.com'}, {'pathPrefix': '/A'}, {'pathPrefix': '/B'}, {'pathPrefix': '/E'}, {'pathPrefix': '/F'}]
- intent: actions=['android.intent.action.VIEW']; categories=['android.intent.category.DEFAULT', 'android.intent.category.BROWSABLE']; data=[{'scheme': 'https'}, {'host': 'click.openai.com'}, {'pathPrefix': '/uni/'}]
- intent: actions=['android.intent.action.VIEW']; categories=['android.intent.category.DEFAULT', 'android.intent.category.BROWSABLE']; data=[{'scheme': 'https'}, {'host': 'u.email.openai.com'}, {'pathPrefix': '/uni/'}]
- intent: actions=['android.intent.action.VIEW']; categories=['android.intent.category.DEFAULT', 'android.intent.category.BROWSABLE']; data=[{'scheme': 'https'}, {'host': 's.openai.com'}, {'pathPrefix': '/uni/'}]
- intent: actions=['android.intent.action.VIEW']; categories=['android.intent.category.DEFAULT', 'android.intent.category.BROWSABLE']; data=[{'scheme': 'https'}, {'host': 'r.openai.com'}, {'pathPrefix': '/uni/'}]
- intent: actions=['android.intent.action.VIEW']; categories=['android.intent.category.DEFAULT', 'android.intent.category.BROWSABLE']; data=[{'scheme': 'https'}, {'scheme': 'http'}, {'host': 'chat.openai.com'}, {'host': 'chatgpt.com'}, {'host': 'chat.com'}, {'host': 'www.chat.com'}, {'host': 'www.chatgpt.com'}, {'host': 'tt.chatgpt.com'}, {'pathPrefix': '/gg/v/'}, {'pathPrefix': '/m/'}, {'path': '/'}, {'path': '/voice'}, {'path': '/voice/'}, {'path': '/tooltip'}, {'path': '/tooltip/'}, {'pathPattern': '/.*/voice'}, {'pathPattern': '/.*/voice/'}, {'path': '/app'}, {'pathPrefix': '/app/'}, {'path': '/open-app'}, {'pathPrefix': '/share/'}, {'pathPrefix': '/share/e/'}, {'pathPrefix': '/c/'}, {'pathPrefix': '/uc/'}, {'path': '/c'}, {'path': '/codex'}, {'path': '/codex/pair'}, {'pathPrefix': '/codex/remote/thread/'}, {'pathPrefix': '/c2/'}, {'pathPrefix': '/subscription'}, {'pathPrefix': '/up/'}, {'pathPrefix': '/g/'}, {'pathPrefix': '/s/c_'}, {'pathPrefix': '/s/m_'}, {'pathPrefix': '/s/p_'}, {'pathPrefix': '/s/t_'}, {'pathPrefix': '/s/w_'}, {'pathPrefix': '/aip/'}, {'pathPrefix': '/image-gen'}, {'pathPrefix': '/images'}, {'path': '/stickers'}, {'path': '/stickers/'}, {'pathPrefix': '/apps'}, {'path': '/discovery-hub'}, {'path': '/discovery-hub/'}, {'path': '/shopping'}, {'path': '/shopping/'}, {'path': '/football'}, {'path': '/football/'}, {'path': '/scheduled'}, {'path': '/scheduled/'}, {'path': '/tasks'}, {'path': '/tasks/'}, {'pathPrefix': '/conversation/oauth_redirect'}, {'pathPrefix': '/settings'}, {'pathPrefix': '/trusted-contact/nominee'}, {'pathPrefix': '/trusted-contact/alert'}, {'pathPrefix': '/trusted-contact/unlinked'}, {'pathPrefix': '/data-controls'}, {'pathPrefix': '/auth-challenge'}, {'pathPrefix': '/feature-interstitial'}, {'pathPrefix': '/announcements'}, {'pathPrefix': '/parentalcontrols'}, {'pathPrefix': '/u18-graduation/teen-unlink'}, {'pathPrefix': '/cfc-verification'}]
- intent: actions=['android.intent.action.VIEW']; categories=['android.intent.category.DEFAULT', 'android.intent.category.BROWSABLE']; data=[{'scheme': 'https'}, {'host': 'chat.openai.com'}, {'host': 'chatgpt.com'}, {'host': 'chat.com'}, {'host': 'www.chat.com'}, {'host': 'www.chatgpt.com'}, {'host': 'tt.chatgpt.com'}, {'pathPrefix': '/s/task_'}, {'pathPrefix': '/s/shareauto_'}]
- intent: actions=['android.intent.action.VIEW']; categories=['android.intent.category.DEFAULT', 'android.intent.category.BROWSABLE']; data=[{'scheme': 'chatgpt'}]

## activity `com.openai.feature.assistant.impl.AssistantProxyActivity`
- exported: `true`
- enabled: `@7F050002`
- intent: actions=['android.intent.action.ASSIST']; categories=['android.intent.category.DEFAULT']; data=[]

## activity `com.openai.voice.assistant.AssistantActivity`
- exported: `true`
- enabled: `<default>`

## activity `com.openai.feature.onboarding.impl.otp.OtpDeepLinkActivity`
- exported: `true`
- enabled: `<default>`
- intent: actions=['android.intent.action.VIEW']; categories=['android.intent.category.DEFAULT', 'android.intent.category.BROWSABLE']; data=[{'scheme': 'https'}, {'host': 'chatgpt.com'}, {'pathPrefix': '/verification-code'}]

## activity `com.openai.feature.onboarding.impl.next.deeplink.ContinueRegistrationActivity`
- exported: `true`
- enabled: `<default>`
- intent: actions=['android.intent.action.VIEW']; categories=['android.intent.category.DEFAULT', 'android.intent.category.BROWSABLE']; data=[{'scheme': 'https'}, {'host': 'chatgpt.com'}, {'pathPrefix': '/continue-registration'}]

## activity `com.openai.feature.auth.impl.web.WebRedirectActivity`
- exported: `true`
- enabled: `<default>`
- intent: actions=['android.intent.action.VIEW']; categories=['android.intent.category.DEFAULT', 'android.intent.category.BROWSABLE']; data=[{'scheme': 'com.openai.chatgpt'}, {'host': 'auth0.openai.com'}, {'host': 'auth0-dev.openai.com'}, {'host': 'auth.openai.com'}, {'host': 'auth.api.openai.org'}, {'pathPrefix': '/android/com.openai.chatgpt/callback'}]

## activity `com.stripe.android.link.LinkRedirectHandlerActivity`
- exported: `true`
- enabled: `<default>`
- intent: actions=['android.intent.action.VIEW']; categories=['android.intent.category.DEFAULT', 'android.intent.category.BROWSABLE']; data=[{'scheme': 'link-popup', 'host': 'complete', 'path': '/com.openai.chatgpt'}]

## activity `com.stripe.android.payments.StripeBrowserProxyReturnActivity`
- exported: `true`
- enabled: `<default>`
- intent: actions=['android.intent.action.VIEW']; categories=['android.intent.category.DEFAULT', 'android.intent.category.BROWSABLE']; data=[{'scheme': 'stripesdk', 'host': 'payment_return_url', 'path': '/com.openai.chatgpt'}]

## activity `com.plaid.internal.redirect.LinkRedirectActivity`
- exported: `true`
- enabled: `<default>`
- intent: actions=['android.intent.action.VIEW']; categories=['android.intent.category.DEFAULT', 'android.intent.category.BROWSABLE']; data=[{'scheme': 'plaid', 'host': 'redirect'}, {'scheme': 'plaid', 'host': 'resume'}]

## activity `com.stripe.android.financialconnections.lite.FinancialConnectionsSheetLiteRedirectActivity`
- exported: `true`
- enabled: `<default>`
- intent: actions=['android.intent.action.VIEW']; categories=['android.intent.category.DEFAULT', 'android.intent.category.BROWSABLE']; data=[{'scheme': 'stripe', 'host': 'financial-connections-lite', 'pathPrefix': '/com.openai.chatgpt/auth_redirect'}]

## activity-alias `com.openai.chatgpt.ImageEditActivity`
- exported: `true`
- enabled: `<default>`
- targetActivity: `com.openai.chatgpt.MainActivity`
- intent: actions=['android.intent.action.EDIT']; categories=['android.intent.category.DEFAULT']; data=[{'scheme': 'content', 'mimeType': 'image/*'}]
- intent: actions=['android.intent.action.EDIT']; categories=['android.intent.category.DEFAULT']; data=[{'scheme': 'file', 'mimeType': 'image/*'}]

## activity-alias `com.openai.chatgpt.FilePreviewActivity`
- exported: `true`
- enabled: `<default>`
- targetActivity: `com.openai.chatgpt.MainActivity`
- intent: actions=['android.intent.action.VIEW']; categories=['android.intent.category.DEFAULT']; data=[{'scheme': 'content', 'mimeType': 'image/*'}, {'scheme': 'content', 'mimeType': 'text/*'}, {'scheme': 'content', 'mimeType': 'application/json'}, {'scheme': 'content', 'mimeType': 'application/ld+json'}, {'scheme': 'content', 'mimeType': 'application/xml'}, {'scheme': 'content', 'mimeType': 'application/javascript'}, {'scheme': 'content', 'mimeType': 'application/x-javascript'}, {'scheme': 'content', 'mimeType': 'application/x-sh'}, {'scheme': 'content', 'mimeType': 'application/x-httpd-php'}, {'scheme': 'content', 'mimeType': 'application/x-yaml'}, {'scheme': 'content', 'mimeType': 'application/yaml'}, {'scheme': 'content', 'mimeType': 'application/pdf'}]
- intent: actions=['android.intent.action.VIEW']; categories=['android.intent.category.DEFAULT']; data=[{'scheme': 'file', 'mimeType': 'image/*'}, {'scheme': 'file', 'mimeType': 'text/*'}, {'scheme': 'file', 'mimeType': 'application/json'}, {'scheme': 'file', 'mimeType': 'application/ld+json'}, {'scheme': 'file', 'mimeType': 'application/xml'}, {'scheme': 'file', 'mimeType': 'application/javascript'}, {'scheme': 'file', 'mimeType': 'application/x-javascript'}, {'scheme': 'file', 'mimeType': 'application/x-sh'}, {'scheme': 'file', 'mimeType': 'application/x-httpd-php'}, {'scheme': 'file', 'mimeType': 'application/x-yaml'}, {'scheme': 'file', 'mimeType': 'application/yaml'}, {'scheme': 'file', 'mimeType': 'application/pdf'}]

## activity-alias `com.openai.chatgpt.TextProcessorActivity`
- exported: `true`
- enabled: `<default>`
- targetActivity: `com.openai.chatgpt.MainActivity`
- intent: actions=['android.intent.action.PROCESS_TEXT']; categories=['android.intent.category.DEFAULT']; data=[{'mimeType': 'text/*'}]

## service `com.openai.feature.assistant.impl.AssistantVoiceInteractionService`
- exported: `true`
- enabled: `@7F050002`
- permission: `android.permission.BIND_VOICE_INTERACTION`
- intent: actions=['android.service.voice.VoiceInteractionService']; categories=[]; data=[]

## service `com.openai.feature.voice.impl.quicktile.QuickTileService`
- exported: `true`
- enabled: `<default>`
- permission: `android.permission.BIND_QUICK_SETTINGS_TILE`
- intent: actions=['android.service.quicksettings.action.QS_TILE']; categories=[]; data=[]

## service `com.openai.feature.conversations.screencontext.ConversationScreenAccessibilityService`
- exported: `true`
- enabled: `<default>`
- permission: `android.permission.BIND_ACCESSIBILITY_SERVICE`
- intent: actions=['android.accessibilityservice.AccessibilityService']; categories=[]; data=[]

## service `com.google.android.gms.auth.api.signin.RevocationBoundService`
- exported: `true`
- enabled: `<default>`
- permission: `com.google.android.gms.auth.api.signin.permission.REVOCATION_NOTIFICATION`

## service `androidx.glance.appwidget.GlanceRemoteViewsService`
- exported: `true`
- enabled: `<default>`
- permission: `android.permission.BIND_REMOTEVIEWS`

## service `androidx.work.impl.background.systemjob.SystemJobService`
- exported: `true`
- enabled: `@7F050005`
- permission: `android.permission.BIND_JOB_SERVICE`

## receiver `com.openai.feature.widget.WidgetReceiver`
- exported: `true`
- enabled: `<default>`
- intent: actions=['android.appwidget.action.APPWIDGET_UPDATE']; categories=[]; data=[]

## receiver `com.openai.feature.widget.WidgetInstallBroadcastReceiver`
- exported: `true`
- enabled: `<default>`

## receiver `com.google.firebase.iid.FirebaseInstanceIdReceiver`
- exported: `true`
- enabled: `<default>`
- permission: `com.google.android.c2dm.permission.SEND`
- intent: actions=['com.google.android.c2dm.intent.RECEIVE']; categories=[]; data=[]

## receiver `androidx.work.impl.diagnostics.DiagnosticsReceiver`
- exported: `true`
- enabled: `true`
- permission: `android.permission.DUMP`
- intent: actions=['androidx.work.diagnostics.REQUEST_DIAGNOSTICS']; categories=[]; data=[]

## receiver `androidx.profileinstaller.ProfileInstallReceiver`
- exported: `true`
- enabled: `true`
- permission: `android.permission.DUMP`
- intent: actions=['androidx.profileinstaller.action.INSTALL_PROFILE']; categories=[]; data=[]
- intent: actions=['androidx.profileinstaller.action.SKIP_FILE']; categories=[]; data=[]
- intent: actions=['androidx.profileinstaller.action.SAVE_PROFILE']; categories=[]; data=[]
- intent: actions=['androidx.profileinstaller.action.BENCHMARK_OPERATION']; categories=[]; data=[]

## provider `com.openai.feature.imagedetail.impl.whatsapp.WhatsAppStickerContentProvider`
- exported: `true`
- enabled: `true`
