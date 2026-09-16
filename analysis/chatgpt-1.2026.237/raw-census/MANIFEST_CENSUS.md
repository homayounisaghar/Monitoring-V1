# Exact manifest census — ChatGPT Android 1.2026.237

Package: `com.openai.chatgpt`

## Requested permissions

- `android.permission.ACCESS_COARSE_LOCATION`
- `android.permission.ACCESS_FINE_LOCATION`
- `android.permission.ACCESS_NETWORK_STATE`
- `android.permission.ACCESS_WIFI_STATE`
- `android.permission.BLUETOOTH`
- `android.permission.CAMERA`
- `android.permission.CHANGE_NETWORK_STATE`
- `android.permission.DETECT_SCREEN_CAPTURE`
- `android.permission.FOREGROUND_SERVICE`
- `android.permission.FOREGROUND_SERVICE_DATA_SYNC`
- `android.permission.FOREGROUND_SERVICE_MEDIA_PROJECTION`
- `android.permission.FOREGROUND_SERVICE_MICROPHONE`
- `android.permission.INTERNET`
- `android.permission.MODIFY_AUDIO_SETTINGS`
- `android.permission.NFC`
- `android.permission.POST_NOTIFICATIONS`
- `android.permission.POST_PROMOTED_NOTIFICATIONS`
- `android.permission.READ_BASIC_PHONE_STATE`
- `android.permission.READ_CONTACTS`
- `android.permission.READ_PHONE_STATE`
- `android.permission.RECEIVE_BOOT_COMPLETED`
- `android.permission.RECORD_AUDIO`
- `android.permission.USE_BIOMETRIC`
- `android.permission.USE_FINGERPRINT`
- `android.permission.VIBRATE`
- `android.permission.WAKE_LOCK`
- `com.android.vending.BILLING`
- `com.google.android.c2dm.permission.RECEIVE`
- `com.google.android.finsky.permission.BIND_GET_INSTALL_REFERRER_SERVICE`
- `com.google.android.gms.permission.AD_ID`
- `com.openai.chatgpt.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION`

## Components and intent filters

### activity: `com.openai.chatgpt.MainActivity`
- exported: `true`; enabled: `<default>`
- filter 1:
  - actions: `android.intent.action.MAIN`
  - categories: `android.intent.category.LAUNCHER`
  - data: _none_
- filter 2:
  - actions: `android.intent.action.SEND`
  - categories: `android.intent.category.DEFAULT`
  - data: `mimeType=image/*`; `mimeType=text/*`; `mimeType=application/*`
- filter 3:
  - actions: `android.intent.action.SEND_MULTIPLE`
  - categories: `android.intent.category.DEFAULT`
  - data: `mimeType=image/*`; `mimeType=text/*`; `mimeType=application/*`

### activity: `com.openai.chatgpt.ChatGptDeeplinkActivity`
- exported: `true`; enabled: `<default>`
- filter 1:
  - actions: `android.intent.action.VIEW`
  - categories: `android.intent.category.DEFAULT`, `android.intent.category.BROWSABLE`
  - data: `scheme=com.openai.chat`; `host=auth`; `pathPattern=/logout`; `pathPattern=/ext_callback`; `pathPattern=/email_verification`
- filter 2:
  - actions: `android.intent.action.VIEW`
  - categories: `android.intent.category.DEFAULT`, `android.intent.category.BROWSABLE`
  - data: `scheme=com.openai.chat, host=codex, path=/open`
- filter 3:
  - actions: `android.intent.action.VIEW`
  - categories: `android.intent.category.DEFAULT`, `android.intent.category.BROWSABLE`
  - data: `scheme=https`; `scheme=http`; `host=platform.openai.com`; `pathPattern=/auth/logout`; `pathPattern=/auth/ext_callback`; `pathPattern=/auth/email_verification`
- filter 4:
  - actions: `android.intent.action.VIEW`
  - categories: `android.intent.category.DEFAULT`, `android.intent.category.BROWSABLE`
  - data: `scheme=https`; `host=link.openai.com`; `pathPrefix=/A`; `pathPrefix=/B`; `pathPrefix=/E`; `pathPrefix=/F`
- filter 5:
  - actions: `android.intent.action.VIEW`
  - categories: `android.intent.category.DEFAULT`, `android.intent.category.BROWSABLE`
  - data: `scheme=https`; `host=click.openai.com`; `pathPrefix=/uni/`
- filter 6:
  - actions: `android.intent.action.VIEW`
  - categories: `android.intent.category.DEFAULT`, `android.intent.category.BROWSABLE`
  - data: `scheme=https`; `host=u.email.openai.com`; `pathPrefix=/uni/`
- filter 7:
  - actions: `android.intent.action.VIEW`
  - categories: `android.intent.category.DEFAULT`, `android.intent.category.BROWSABLE`
  - data: `scheme=https`; `host=s.openai.com`; `pathPrefix=/uni/`
- filter 8:
  - actions: `android.intent.action.VIEW`
  - categories: `android.intent.category.DEFAULT`, `android.intent.category.BROWSABLE`
  - data: `scheme=https`; `host=r.openai.com`; `pathPrefix=/uni/`
- filter 9:
  - actions: `android.intent.action.VIEW`
  - categories: `android.intent.category.DEFAULT`, `android.intent.category.BROWSABLE`
  - data: `scheme=https`; `scheme=http`; `host=chat.openai.com`; `host=chatgpt.com`; `host=chat.com`; `host=www.chat.com`; `host=www.chatgpt.com`; `host=tt.chatgpt.com`; `pathPrefix=/gg/v/`; `pathPrefix=/m/`; `path=/`; `path=/voice`; `path=/voice/`; `path=/tooltip`; `path=/tooltip/`; `pathPattern=/.*/voice`; `pathPattern=/.*/voice/`; `path=/app`; `pathPrefix=/app/`; `path=/open-app`; `pathPrefix=/share/`; `pathPrefix=/share/e/`; `pathPrefix=/c/`; `pathPrefix=/uc/`; `path=/c`; `path=/codex`; `path=/codex/pair`; `pathPrefix=/codex/remote/thread/`; `pathPrefix=/c2/`; `pathPrefix=/subscription`; `pathPrefix=/up/`; `pathPrefix=/g/`; `pathPrefix=/s/c_`; `pathPrefix=/s/m_`; `pathPrefix=/s/p_`; `pathPrefix=/s/t_`; `pathPrefix=/s/w_`; `pathPrefix=/aip/`; `pathPrefix=/image-gen`; `pathPrefix=/images`; `path=/stickers`; `path=/stickers/`; `pathPrefix=/apps`; `path=/discovery-hub`; `path=/discovery-hub/`; `path=/shopping`; `path=/shopping/`; `path=/football`; `path=/football/`; `path=/scheduled`; `path=/scheduled/`; `path=/tasks`; `path=/tasks/`; `pathPrefix=/conversation/oauth_redirect`; `pathPrefix=/settings`; `pathPrefix=/trusted-contact/nominee`; `pathPrefix=/trusted-contact/alert`; `pathPrefix=/trusted-contact/unlinked`; `pathPrefix=/data-controls`; `pathPrefix=/auth-challenge`; `pathPrefix=/feature-interstitial`; `pathPrefix=/announcements`; `pathPrefix=/parentalcontrols`; `pathPrefix=/u18-graduation/teen-unlink`; `pathPrefix=/cfc-verification`
- filter 10:
  - actions: `android.intent.action.VIEW`
  - categories: `android.intent.category.DEFAULT`, `android.intent.category.BROWSABLE`
  - data: `scheme=https`; `host=chat.openai.com`; `host=chatgpt.com`; `host=chat.com`; `host=www.chat.com`; `host=www.chatgpt.com`; `host=tt.chatgpt.com`; `pathPrefix=/s/task_`; `pathPrefix=/s/shareauto_`
- filter 11:
  - actions: `android.intent.action.VIEW`
  - categories: `android.intent.category.DEFAULT`, `android.intent.category.BROWSABLE`
  - data: `scheme=chatgpt`

### activity: `com.openai.feature.assistant.impl.AssistantProxyActivity`
- exported: `true`; enabled: `@7F050002`
- filter 1:
  - actions: `android.intent.action.ASSIST`
  - categories: `android.intent.category.DEFAULT`
  - data: _none_

### activity: `com.openai.feature.codexremote.impl.CodexRemoteBubbleActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.openai.feature.conversations.screencontext.ConversationScreenShareSettingsGuideActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.openai.voice.assistant.AssistantActivity`
- exported: `true`; enabled: `<default>`
- intent filters: none

### activity: `com.openai.feature.sites.impl.SitesShareActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.openai.feature.onboarding.impl.otp.OtpDeepLinkActivity`
- exported: `true`; enabled: `<default>`
- filter 1:
  - actions: `android.intent.action.VIEW`
  - categories: `android.intent.category.DEFAULT`, `android.intent.category.BROWSABLE`
  - data: `scheme=https`; `host=chatgpt.com`; `pathPrefix=/verification-code`

### activity: `com.openai.feature.onboarding.impl.next.deeplink.ContinueRegistrationActivity`
- exported: `true`; enabled: `<default>`
- filter 1:
  - actions: `android.intent.action.VIEW`
  - categories: `android.intent.category.DEFAULT`, `android.intent.category.BROWSABLE`
  - data: `scheme=https`; `host=chatgpt.com`; `pathPrefix=/continue-registration`

### activity: `com.openai.feature.auth.impl.web.WebAuthenticationActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.openai.feature.auth.impl.web.WebRedirectActivity`
- exported: `true`; enabled: `<default>`
- filter 1:
  - actions: `android.intent.action.VIEW`
  - categories: `android.intent.category.DEFAULT`, `android.intent.category.BROWSABLE`
  - data: `scheme=com.openai.chatgpt`; `host=auth0.openai.com`; `host=auth0-dev.openai.com`; `host=auth.openai.com`; `host=auth.api.openai.org`; `pathPrefix=/android/com.openai.chatgpt/callback`

### activity: `com.withpersona.sdk2.inquiry.internal.InquiryActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.google.android.libraries.places.widget.AutocompleteActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.google.android.libraries.places.widget.BasicPlaceAutocompleteActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.google.android.libraries.places.widget.PlaceAutocompleteActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.google.android.libraries.places.widget.internal.placedetails.photoviewer.PlacesLightboxActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.stripe.android.paymentsheet.PaymentSheetActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.stripe.android.paymentsheet.PaymentOptionsActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.stripe.android.customersheet.CustomerSheetActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.stripe.android.paymentsheet.addresselement.AddressElementActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.stripe.android.paymentsheet.addresselement.AutocompleteActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.stripe.android.paymentsheet.paymentdatacollection.bacs.BacsMandateConfirmationActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.stripe.android.paymentsheet.paymentdatacollection.polling.PollingActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.stripe.android.paymentsheet.ui.SepaMandateActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.stripe.android.paymentsheet.ExternalPaymentMethodProxyActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.stripe.android.paymentelement.confirmation.cpms.CustomPaymentMethodProxyActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.stripe.android.paymentsheet.paymentdatacollection.cvcrecollection.CvcRecollectionActivity`
- exported: `<unspecified>`; enabled: `<default>`
- intent filters: none

### activity: `com.stripe.android.paymentelement.embedded.sheet.EmbeddedSheetActivity`
- exported: `<unspecified>`; enabled: `<default>`
- intent filters: none

### activity: `com.stripe.android.common.nfcscan.NfcScanningActivity`
- exported: `<unspecified>`; enabled: `<default>`
- intent filters: none

### activity: `com.stripe.android.common.taptoadd.TapToAddActivity`
- exported: `<unspecified>`; enabled: `<default>`
- intent filters: none

### activity: `com.stripe.android.attestation.AttestationActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.stripe.android.link.LinkActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.stripe.android.link.LinkForegroundActivity`
- exported: `<unspecified>`; enabled: `<default>`
- intent filters: none

### activity: `com.stripe.android.link.LinkRedirectHandlerActivity`
- exported: `true`; enabled: `<default>`
- filter 1:
  - actions: `android.intent.action.VIEW`
  - categories: `android.intent.category.DEFAULT`, `android.intent.category.BROWSABLE`
  - data: `scheme=link-popup, host=complete, path=/com.openai.chatgpt`

### activity: `com.stripe.android.view.PaymentAuthWebViewActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.stripe.android.view.PaymentRelayActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.stripe.android.payments.StripeBrowserLauncherActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.stripe.android.payments.StripeBrowserProxyReturnActivity`
- exported: `true`; enabled: `<default>`
- filter 1:
  - actions: `android.intent.action.VIEW`
  - categories: `android.intent.category.DEFAULT`, `android.intent.category.BROWSABLE`
  - data: `scheme=stripesdk, host=payment_return_url, path=/com.openai.chatgpt`

### activity: `com.stripe.android.payments.core.authentication.threeds2.Stripe3ds2TransactionActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.stripe.android.googlepaylauncher.GooglePayLauncherActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.stripe.android.googlepaylauncher.GooglePayPaymentMethodLauncherActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.stripe.android.payments.paymentlauncher.PaymentLauncherConfirmationActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.stripe.android.payments.bankaccount.ui.CollectBankAccountActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.stripe.android.challenge.passive.PassiveChallengeActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.stripe.android.challenge.passive.warmer.activity.PassiveChallengeWarmerActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.stripe.android.challenge.confirmation.IntentConfirmationChallengeActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.stripe.android.stripe3ds2.views.ChallengeActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `androidx.credentials.playservices.controllers.identityauth.HiddenActivity`
- exported: `false`; enabled: `true`
- intent filters: none

### activity: `androidx.credentials.playservices.controllers.identitycredentials.IdentityCredentialApiHiddenActivity`
- exported: `false`; enabled: `true`
- intent filters: none

### activity: `com.plaid.internal.link.LinkActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.plaid.internal.redirect.LinkRedirectActivity`
- exported: `true`; enabled: `<default>`
- filter 1:
  - actions: `android.intent.action.VIEW`
  - categories: `android.intent.category.DEFAULT`, `android.intent.category.BROWSABLE`
  - data: `scheme=plaid, host=redirect`; `scheme=plaid, host=resume`

### activity: `com.google.android.gms.auth.api.signin.internal.SignInHubActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.stripe.android.financialconnections.lite.FinancialConnectionsSheetLiteRedirectActivity`
- exported: `true`; enabled: `<default>`
- filter 1:
  - actions: `android.intent.action.VIEW`
  - categories: `android.intent.category.DEFAULT`, `android.intent.category.BROWSABLE`
  - data: `scheme=stripe, host=financial-connections-lite, pathPrefix=/com.openai.chatgpt/auth_redirect`

### activity: `com.stripe.android.financialconnections.lite.FinancialConnectionsSheetLiteActivity`
- exported: `<unspecified>`; enabled: `<default>`
- intent filters: none

### activity: `com.revenuecat.purchases.amazon.purchasing.ProxyAmazonBillingActivity`
- exported: `<unspecified>`; enabled: `<default>`
- intent filters: none

### activity: `com.revenuecat.purchases.SimulatedStoreErrorDialogActivity`
- exported: `<unspecified>`; enabled: `<default>`
- intent filters: none

### activity: `com.android.billingclient.api.ProxyBillingActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.android.billingclient.api.ProxyBillingActivityV2`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `androidx.glance.appwidget.action.ActionTrampolineActivity`
- exported: `false`; enabled: `true`
- intent filters: none

### activity: `androidx.glance.appwidget.action.InvisibleActionTrampolineActivity`
- exported: `false`; enabled: `true`
- intent filters: none

### activity: `com.google.android.gms.common.api.GoogleApiActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity: `com.google.android.play.core.common.PlayCoreDialogWrapperActivity`
- exported: `false`; enabled: `<default>`
- intent filters: none

### activity-alias: `com.openai.chatgpt.ImageEditActivity`
- exported: `true`; enabled: `<default>`
- filter 1:
  - actions: `android.intent.action.EDIT`
  - categories: `android.intent.category.DEFAULT`
  - data: `scheme=content, mimeType=image/*`
- filter 2:
  - actions: `android.intent.action.EDIT`
  - categories: `android.intent.category.DEFAULT`
  - data: `scheme=file, mimeType=image/*`

### activity-alias: `com.openai.chatgpt.FilePreviewActivity`
- exported: `true`; enabled: `<default>`
- filter 1:
  - actions: `android.intent.action.VIEW`
  - categories: `android.intent.category.DEFAULT`
  - data: `scheme=content, mimeType=image/*`; `scheme=content, mimeType=text/*`; `scheme=content, mimeType=application/json`; `scheme=content, mimeType=application/ld+json`; `scheme=content, mimeType=application/xml`; `scheme=content, mimeType=application/javascript`; `scheme=content, mimeType=application/x-javascript`; `scheme=content, mimeType=application/x-sh`; `scheme=content, mimeType=application/x-httpd-php`; `scheme=content, mimeType=application/x-yaml`; `scheme=content, mimeType=application/yaml`; `scheme=content, mimeType=application/pdf`
- filter 2:
  - actions: `android.intent.action.VIEW`
  - categories: `android.intent.category.DEFAULT`
  - data: `scheme=file, mimeType=image/*`; `scheme=file, mimeType=text/*`; `scheme=file, mimeType=application/json`; `scheme=file, mimeType=application/ld+json`; `scheme=file, mimeType=application/xml`; `scheme=file, mimeType=application/javascript`; `scheme=file, mimeType=application/x-javascript`; `scheme=file, mimeType=application/x-sh`; `scheme=file, mimeType=application/x-httpd-php`; `scheme=file, mimeType=application/x-yaml`; `scheme=file, mimeType=application/yaml`; `scheme=file, mimeType=application/pdf`

### activity-alias: `com.openai.chatgpt.TextProcessorActivity`
- exported: `true`; enabled: `<default>`
- filter 1:
  - actions: `android.intent.action.PROCESS_TEXT`
  - categories: `android.intent.category.DEFAULT`
  - data: `mimeType=text/*`

### service: `androidx.appcompat.app.AppLocalesMetadataHolderService`
- exported: `false`; enabled: `false`
- intent filters: none

### service: `com.openai.feature.assistant.impl.AssistantVoiceInteractionService`
- exported: `true`; enabled: `@7F050002`; permission: `android.permission.BIND_VOICE_INTERACTION`
- filter 1:
  - actions: `android.service.voice.VoiceInteractionService`
  - categories: _none_
  - data: _none_

### service: `com.openai.feature.assistant.impl.AssistantVoiceInteractionSessionService`
- exported: `<unspecified>`; enabled: `@7F050002`; permission: `android.permission.BIND_VOICE_INTERACTION`
- intent filters: none

### service: `com.openai.feature.conversations.impl.coordinator.ConversationStreamingService`
- exported: `false`; enabled: `<default>`
- intent filters: none

### service: `com.openai.feature.conversations.impl.notifications.WorkReasoningNotificationForegroundService`
- exported: `false`; enabled: `<default>`
- intent filters: none

### service: `com.openai.feature.voice.impl.quicktile.QuickTileService`
- exported: `true`; enabled: `<default>`; permission: `android.permission.BIND_QUICK_SETTINGS_TILE`
- filter 1:
  - actions: `android.service.quicksettings.action.QS_TILE`
  - categories: _none_
  - data: _none_

### service: `com.openai.feature.codexremote.impl.data.CodexRemoteSessionForegroundService`
- exported: `false`; enabled: `<default>`
- intent filters: none

### service: `com.openai.feature.codexremote.impl.voice.CodexVoiceForegroundService`
- exported: `false`; enabled: `<default>`
- intent filters: none

### service: `com.openai.feature.conversations.screencontext.ConversationScreenAccessibilityService`
- exported: `true`; enabled: `<default>`; permission: `android.permission.BIND_ACCESSIBILITY_SERVICE`
- filter 1:
  - actions: `android.accessibilityservice.AccessibilityService`
  - categories: _none_
  - data: _none_

### service: `com.openai.feature.notification.impl.NotificationService`
- exported: `false`; enabled: `<default>`
- filter 1:
  - actions: `com.google.firebase.MESSAGING_EVENT`
  - categories: _none_
  - data: _none_

### service: `com.openai.voice.webrtc.VoiceModeForegroundService`
- exported: `false`; enabled: `<default>`
- intent filters: none

### service: `androidx.camera.core.impl.MetadataHolderService`
- exported: `false`; enabled: `false`
- intent filters: none

### service: `androidx.credentials.playservices.CredentialProviderMetadataHolder`
- exported: `false`; enabled: `true`
- intent filters: none

### service: `com.google.firebase.components.ComponentDiscoveryService`
- exported: `false`; enabled: `<default>`
- intent filters: none

### service: `com.google.android.gms.auth.api.signin.RevocationBoundService`
- exported: `true`; enabled: `<default>`; permission: `com.google.android.gms.auth.api.signin.permission.REVOCATION_NOTIFICATION`
- intent filters: none

### service: `com.google.firebase.messaging.FirebaseMessagingService`
- exported: `false`; enabled: `<default>`
- filter 1:
  - actions: `com.google.firebase.MESSAGING_EVENT`
  - categories: _none_
  - data: _none_

### service: `com.google.mlkit.common.internal.MlKitComponentDiscoveryService`
- exported: `false`; enabled: `<default>`
- intent filters: none

### service: `androidx.glance.appwidget.GlanceRemoteViewsService`
- exported: `true`; enabled: `<default>`; permission: `android.permission.BIND_REMOTEVIEWS`
- intent filters: none

### service: `androidx.work.impl.background.systemjob.SystemJobService`
- exported: `true`; enabled: `@7F050005`; permission: `android.permission.BIND_JOB_SERVICE`
- intent filters: none

### service: `androidx.work.impl.foreground.SystemForegroundService`
- exported: `false`; enabled: `@7F050004`
- intent filters: none

### service: `androidx.room.MultiInstanceInvalidationService`
- exported: `false`; enabled: `<default>`
- intent filters: none

### service: `androidx.core.widget.RemoteViewsCompatService`
- exported: `<unspecified>`; enabled: `<default>`; permission: `android.permission.BIND_REMOTEVIEWS`
- intent filters: none

### service: `com.google.android.datatransport.runtime.backends.TransportBackendDiscovery`
- exported: `false`; enabled: `<default>`
- intent filters: none

### service: `com.google.android.datatransport.runtime.scheduling.jobscheduling.JobInfoSchedulerService`
- exported: `false`; enabled: `<default>`; permission: `android.permission.BIND_JOB_SERVICE`
- intent filters: none

### receiver: `com.openai.apps.appbase.app.managedconfig.ManagedConfigurationsChangedReceiver`
- exported: `false`; enabled: `<default>`
- filter 1:
  - actions: `android.intent.action.APPLICATION_RESTRICTIONS_CHANGED`
  - categories: _none_
  - data: _none_

### receiver: `com.openai.feature.calpico.impl.notification.CalpicoNotificationBroadcastReceiver`
- exported: `false`; enabled: `<default>`
- intent filters: none

### receiver: `com.openai.feature.shortcut.impl.PinnedShortcutReceiver`
- exported: `false`; enabled: `<default>`
- intent filters: none

### receiver: `com.openai.feature.notification.ConversationBubbleDeletedReceiver`
- exported: `false`; enabled: `<default>`
- intent filters: none

### receiver: `com.openai.feature.notification.impl.NotificationBroadcastReceiver`
- exported: `false`; enabled: `<default>`
- intent filters: none

### receiver: `com.openai.feature.notification.impl.AppUpdateReceiver`
- exported: `false`; enabled: `false`
- filter 1:
  - actions: `android.intent.action.MY_PACKAGE_REPLACED`
  - categories: _none_
  - data: _none_

### receiver: `com.openai.feature.widget.WidgetReceiver`
- exported: `true`; enabled: `<default>`
- filter 1:
  - actions: `android.appwidget.action.APPWIDGET_UPDATE`
  - categories: _none_
  - data: _none_

### receiver: `com.openai.feature.widget.WidgetInstallBroadcastReceiver`
- exported: `true`; enabled: `<default>`
- intent filters: none

### receiver: `com.google.firebase.iid.FirebaseInstanceIdReceiver`
- exported: `true`; enabled: `<default>`; permission: `com.google.android.c2dm.permission.SEND`
- filter 1:
  - actions: `com.google.android.c2dm.intent.RECEIVE`
  - categories: _none_
  - data: _none_

### receiver: `androidx.glance.appwidget.action.ActionCallbackBroadcastReceiver`
- exported: `false`; enabled: `true`
- intent filters: none

### receiver: `androidx.glance.appwidget.UnmanagedSessionReceiver`
- exported: `false`; enabled: `true`
- intent filters: none

### receiver: `androidx.glance.appwidget.MyPackageReplacedReceiver`
- exported: `false`; enabled: `true`
- filter 1:
  - actions: `android.intent.action.MY_PACKAGE_REPLACED`
  - categories: _none_
  - data: _none_

### receiver: `androidx.work.impl.utils.ForceStopRunnable$BroadcastReceiver`
- exported: `false`; enabled: `true`
- intent filters: none

### receiver: `androidx.work.impl.background.systemalarm.RescheduleReceiver`
- exported: `false`; enabled: `false`
- filter 1:
  - actions: `android.intent.action.BOOT_COMPLETED`
  - categories: _none_
  - data: _none_

### receiver: `androidx.work.impl.diagnostics.DiagnosticsReceiver`
- exported: `true`; enabled: `true`; permission: `android.permission.DUMP`
- filter 1:
  - actions: `androidx.work.diagnostics.REQUEST_DIAGNOSTICS`
  - categories: _none_
  - data: _none_

### receiver: `androidx.profileinstaller.ProfileInstallReceiver`
- exported: `true`; enabled: `true`; permission: `android.permission.DUMP`
- filter 1:
  - actions: `androidx.profileinstaller.action.INSTALL_PROFILE`
  - categories: _none_
  - data: _none_
- filter 2:
  - actions: `androidx.profileinstaller.action.SKIP_FILE`
  - categories: _none_
  - data: _none_
- filter 3:
  - actions: `androidx.profileinstaller.action.SAVE_PROFILE`
  - categories: _none_
  - data: _none_
- filter 4:
  - actions: `androidx.profileinstaller.action.BENCHMARK_OPERATION`
  - categories: _none_
  - data: _none_

### receiver: `com.google.android.datatransport.runtime.scheduling.jobscheduling.AlarmManagerSchedulerBroadcastReceiver`
- exported: `false`; enabled: `<default>`
- intent filters: none

### provider: `com.openai.apps.appbase.app.startup.FirebaseInitProvider`
- exported: `false`; enabled: `<default>`
- intent filters: none

### provider: `com.openai.feature.imagedetail.impl.whatsapp.WhatsAppStickerContentProvider`
- exported: `true`; enabled: `true`
- intent filters: none

### provider: `com.openai.files.ChatFileProvider`
- exported: `false`; enabled: `<default>`
- intent filters: none

### provider: `com.openai.draw.GlyphsFileProvider`
- exported: `false`; enabled: `<default>`
- intent filters: none

### provider: `com.withpersona.sdk2.inquiry.DocumentFileProvider`
- exported: `false`; enabled: `<default>`
- intent filters: none

### provider: `com.plaid.internal.webview.PlaidFileProvider`
- exported: `false`; enabled: `<default>`
- intent filters: none

### provider: `androidx.startup.InitializationProvider`
- exported: `false`; enabled: `<default>`
- intent filters: none

### provider: `androidx.core.content.FileProvider`
- exported: `false`; enabled: `<default>`
- intent filters: none

### provider: `com.google.mlkit.common.internal.MlKitInitProvider`
- exported: `false`; enabled: `<default>`
- intent filters: none

### provider: `org.jetbrains.compose.resources.AndroidContextProvider`
- exported: `false`; enabled: `true`
- intent filters: none

### provider: `papa.internal.PerfsAppStartListener`
- exported: `false`; enabled: `<default>`
- intent filters: none

### provider: `com.datadog.android.rum.DdRumContentProvider`
- exported: `false`; enabled: `<default>`
- intent filters: none

### provider: `io.sentry.ndk.SentryNdkPreloadProvider`
- exported: `false`; enabled: `<default>`
- intent filters: none

## Exported components summary

- `activity` `com.openai.chatgpt.MainActivity`
- `activity` `com.openai.chatgpt.ChatGptDeeplinkActivity`
- `activity` `com.openai.feature.assistant.impl.AssistantProxyActivity`
- `activity` `com.openai.voice.assistant.AssistantActivity`
- `activity` `com.openai.feature.onboarding.impl.otp.OtpDeepLinkActivity`
- `activity` `com.openai.feature.onboarding.impl.next.deeplink.ContinueRegistrationActivity`
- `activity` `com.openai.feature.auth.impl.web.WebRedirectActivity`
- `activity` `com.stripe.android.link.LinkRedirectHandlerActivity`
- `activity` `com.stripe.android.payments.StripeBrowserProxyReturnActivity`
- `activity` `com.plaid.internal.redirect.LinkRedirectActivity`
- `activity` `com.stripe.android.financialconnections.lite.FinancialConnectionsSheetLiteRedirectActivity`
- `activity-alias` `com.openai.chatgpt.ImageEditActivity`
- `activity-alias` `com.openai.chatgpt.FilePreviewActivity`
- `activity-alias` `com.openai.chatgpt.TextProcessorActivity`
- `service` `com.openai.feature.assistant.impl.AssistantVoiceInteractionService` — permission `android.permission.BIND_VOICE_INTERACTION`
- `service` `com.openai.feature.voice.impl.quicktile.QuickTileService` — permission `android.permission.BIND_QUICK_SETTINGS_TILE`
- `service` `com.openai.feature.conversations.screencontext.ConversationScreenAccessibilityService` — permission `android.permission.BIND_ACCESSIBILITY_SERVICE`
- `service` `com.google.android.gms.auth.api.signin.RevocationBoundService` — permission `com.google.android.gms.auth.api.signin.permission.REVOCATION_NOTIFICATION`
- `service` `androidx.glance.appwidget.GlanceRemoteViewsService` — permission `android.permission.BIND_REMOTEVIEWS`
- `service` `androidx.work.impl.background.systemjob.SystemJobService` — permission `android.permission.BIND_JOB_SERVICE`
- `receiver` `com.openai.feature.widget.WidgetReceiver`
- `receiver` `com.openai.feature.widget.WidgetInstallBroadcastReceiver`
- `receiver` `com.google.firebase.iid.FirebaseInstanceIdReceiver` — permission `com.google.android.c2dm.permission.SEND`
- `receiver` `androidx.work.impl.diagnostics.DiagnosticsReceiver` — permission `android.permission.DUMP`
- `receiver` `androidx.profileinstaller.ProfileInstallReceiver` — permission `android.permission.DUMP`
- `provider` `com.openai.feature.imagedetail.impl.whatsapp.WhatsAppStickerContentProvider`

## Share / process-text candidates

- `activity` `com.openai.chatgpt.MainActivity` exported=`true` actions=['android.intent.action.SEND'] data=['mimeType=image/*', 'mimeType=text/*', 'mimeType=application/*']
- `activity` `com.openai.chatgpt.MainActivity` exported=`true` actions=['android.intent.action.SEND_MULTIPLE'] data=['mimeType=image/*', 'mimeType=text/*', 'mimeType=application/*']
- `activity` `com.openai.chatgpt.ChatGptDeeplinkActivity` exported=`true` actions=['android.intent.action.VIEW'] data=['scheme=https', 'scheme=http', 'host=chat.openai.com', 'host=chatgpt.com', 'host=chat.com', 'host=www.chat.com', 'host=www.chatgpt.com', 'host=tt.chatgpt.com', 'pathPrefix=/gg/v/', 'pathPrefix=/m/', 'path=/', 'path=/voice', 'path=/voice/', 'path=/tooltip', 'path=/tooltip/', 'pathPattern=/.*/voice', 'pathPattern=/.*/voice/', 'path=/app', 'pathPrefix=/app/', 'path=/open-app', 'pathPrefix=/share/', 'pathPrefix=/share/e/', 'pathPrefix=/c/', 'pathPrefix=/uc/', 'path=/c', 'path=/codex', 'path=/codex/pair', 'pathPrefix=/codex/remote/thread/', 'pathPrefix=/c2/', 'pathPrefix=/subscription', 'pathPrefix=/up/', 'pathPrefix=/g/', 'pathPrefix=/s/c_', 'pathPrefix=/s/m_', 'pathPrefix=/s/p_', 'pathPrefix=/s/t_', 'pathPrefix=/s/w_', 'pathPrefix=/aip/', 'pathPrefix=/image-gen', 'pathPrefix=/images', 'path=/stickers', 'path=/stickers/', 'pathPrefix=/apps', 'path=/discovery-hub', 'path=/discovery-hub/', 'path=/shopping', 'path=/shopping/', 'path=/football', 'path=/football/', 'path=/scheduled', 'path=/scheduled/', 'path=/tasks', 'path=/tasks/', 'pathPrefix=/conversation/oauth_redirect', 'pathPrefix=/settings', 'pathPrefix=/trusted-contact/nominee', 'pathPrefix=/trusted-contact/alert', 'pathPrefix=/trusted-contact/unlinked', 'pathPrefix=/data-controls', 'pathPrefix=/auth-challenge', 'pathPrefix=/feature-interstitial', 'pathPrefix=/announcements', 'pathPrefix=/parentalcontrols', 'pathPrefix=/u18-graduation/teen-unlink', 'pathPrefix=/cfc-verification']
- `activity` `com.openai.chatgpt.ChatGptDeeplinkActivity` exported=`true` actions=['android.intent.action.VIEW'] data=['scheme=https', 'host=chat.openai.com', 'host=chatgpt.com', 'host=chat.com', 'host=www.chat.com', 'host=www.chatgpt.com', 'host=tt.chatgpt.com', 'pathPrefix=/s/task_', 'pathPrefix=/s/shareauto_']
- `activity-alias` `com.openai.chatgpt.TextProcessorActivity` exported=`true` actions=['android.intent.action.PROCESS_TEXT'] data=['mimeType=text/*']

## Voice / assistant candidates

- `activity` `com.openai.chatgpt.ChatGptDeeplinkActivity` exported=`true` actions=['android.intent.action.VIEW'] data=['scheme=https', 'scheme=http', 'host=chat.openai.com', 'host=chatgpt.com', 'host=chat.com', 'host=www.chat.com', 'host=www.chatgpt.com', 'host=tt.chatgpt.com', 'pathPrefix=/gg/v/', 'pathPrefix=/m/', 'path=/', 'path=/voice', 'path=/voice/', 'path=/tooltip', 'path=/tooltip/', 'pathPattern=/.*/voice', 'pathPattern=/.*/voice/', 'path=/app', 'pathPrefix=/app/', 'path=/open-app', 'pathPrefix=/share/', 'pathPrefix=/share/e/', 'pathPrefix=/c/', 'pathPrefix=/uc/', 'path=/c', 'path=/codex', 'path=/codex/pair', 'pathPrefix=/codex/remote/thread/', 'pathPrefix=/c2/', 'pathPrefix=/subscription', 'pathPrefix=/up/', 'pathPrefix=/g/', 'pathPrefix=/s/c_', 'pathPrefix=/s/m_', 'pathPrefix=/s/p_', 'pathPrefix=/s/t_', 'pathPrefix=/s/w_', 'pathPrefix=/aip/', 'pathPrefix=/image-gen', 'pathPrefix=/images', 'path=/stickers', 'path=/stickers/', 'pathPrefix=/apps', 'path=/discovery-hub', 'path=/discovery-hub/', 'path=/shopping', 'path=/shopping/', 'path=/football', 'path=/football/', 'path=/scheduled', 'path=/scheduled/', 'path=/tasks', 'path=/tasks/', 'pathPrefix=/conversation/oauth_redirect', 'pathPrefix=/settings', 'pathPrefix=/trusted-contact/nominee', 'pathPrefix=/trusted-contact/alert', 'pathPrefix=/trusted-contact/unlinked', 'pathPrefix=/data-controls', 'pathPrefix=/auth-challenge', 'pathPrefix=/feature-interstitial', 'pathPrefix=/announcements', 'pathPrefix=/parentalcontrols', 'pathPrefix=/u18-graduation/teen-unlink', 'pathPrefix=/cfc-verification']
- `activity` `com.openai.feature.assistant.impl.AssistantProxyActivity` exported=`true` actions=['android.intent.action.ASSIST'] data=[]
- `service` `com.openai.feature.assistant.impl.AssistantVoiceInteractionService` exported=`true` actions=['android.service.voice.VoiceInteractionService'] data=[]
- `service` `com.openai.feature.voice.impl.quicktile.QuickTileService` exported=`true` actions=['android.service.quicksettings.action.QS_TILE'] data=[]

## Package visibility queries

- `intent` {}
- `intent` {}
- `intent` {}
- `intent` {}
- `intent` {}
- `intent` {}
- `package` {'name': 'com.google.android.gm'}
- `package` {'name': 'com.google.android.gm.lite'}
- `package` {'name': 'com.microsoft.office.outlook'}
- `package` {'name': 'com.google.android.apps.messaging'}
- `package` {'name': 'com.samsung.android.messaging'}
- `package` {'name': 'com.android.mms'}
- `package` {'name': 'com.instagram.android'}
- `package` {'name': 'com.instagram.lite'}
- `package` {'name': 'com.facebook.orca'}
- `package` {'name': 'com.facebook.mlite'}
- `package` {'name': 'com.facebook.katana'}
- `package` {'name': 'com.whatsapp'}
- `package` {'name': 'com.whatsapp.w4b'}
- `package` {'name': 'org.telegram.messenger'}
- `package` {'name': 'org.thunderdog.challegram'}
- `package` {'name': 'org.thoughtcrime.securesms'}
- `package` {'name': 'com.kakao.talk'}
- `package` {'name': 'jp.naver.line.android'}
- `package` {'name': 'com.snapchat.android'}
- `package` {'name': 'com.samsung.android.email.provider'}
- `package` {'name': 'com.yahoo.mobile.client.android.mail'}
- `package` {'name': 'com.zhiliaoapp.musically'}
- `package` {'name': 'com.ss.android.ugc.trill'}
- `package` {'name': 'com.twitter.android'}
- `intent` {}
- `package` {'name': 'com.android.vending'}
- `package` {'name': 'com.google.android.gms'}
- `intent` {}
- `intent` {}
- `intent` {}
- `intent` {}
- `intent` {}
- `intent` {}
- `package` {'name': 'com.heytap.market'}
- `package` {'name': 'com.oppo.market'}
- `provider` {'authorities': 'com.heytap.market.ExpTrackProvider'}
- `provider` {'authorities': 'com.vivo.attribution.provider'}
- `package` {'name': 'com.android.chrome'}
- `intent` {}
- `intent` {}
- `package` {'name': 'com.google.android.apps.maps'}