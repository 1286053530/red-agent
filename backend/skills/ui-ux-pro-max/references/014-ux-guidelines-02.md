44,Accessibility,Error Messages,All,Error messages must be announced,Use aria-live or role=alert for errors,Visual-only error indication,role='alert',Red border only,High
45,Accessibility,Skip Links,Web,Allow keyboard users to skip navigation,Provide skip to main content link,No skip link on nav-heavy pages,Skip to main content link,100 tabs to reach content,Medium
46,Performance,Image Optimization,All,Large images slow page load,Use appropriate size and format (WebP),Unoptimized full-size images,srcset with multiple sizes,4000px image for 400px display,High
47,Performance,Lazy Loading,All,Load content as needed,Lazy load below-fold images and content,Load everything upfront,loading='lazy',All images eager load,Medium
48,Performance,Code Splitting,Web,Large bundles slow initial load,Split code by route/feature,Single large bundle,dynamic import(),All code in main bundle,Medium
49,Performance,Caching,Web,Repeat visits should be fast,Set appropriate cache headers,No caching strategy,Cache-Control headers,Every request hits server,Medium
50,Performance,Font Loading,Web,Web fonts can block rendering,Use font-display swap or optional,Invisible text during font load,font-display: swap,FOIT (Flash of Invisible Text),Medium
51,Performance,Third Party Scripts,Web,External scripts can block rendering,Load non-critical scripts async/defer,Synchronous third-party scripts,async or defer attribute,<script src='...'> in head,Medium
52,Performance,Bundle Size,Web,Large JavaScript slows interaction,Monitor and minimize bundle size,Ignore bundle size growth,Bundle analyzer,No size monitoring,Medium
53,Performance,Render Blocking,Web,CSS/JS can block first paint,Inline critical CSS defer non-critical,Large blocking CSS files,Critical CSS inline,All CSS in head,Medium
54,Forms,Input Labels,All,Every input needs a visible label,Always show label above or beside input,Placeholder as only label,<label>Email</label><input>,placeholder='Email' only,High
55,Forms,Error Placement,All,Each invalid field needs an inline error connected to that field,Show a specific error below the input and reference it with aria-describedby,Show only a top-level error without identifying each invalid field,"<input aria-describedby=""email-error""><p id=""email-error"">Enter an email address</p>",Red border or summary only,High
56,Forms,Inline Validation,All,Validate as user types or on blur,Validate on blur for most fields,Validate only on submit,onBlur validation,Submit-only validation,Medium
57,Forms,Input Types,All,Use appropriate input types,Use email tel number url etc,Text input for everything,type='email',type='text' for email,Medium
58,Forms,Autofill Support,Web,Help browsers autofill correctly,Use autocomplete attribute properly,Block or ignore autofill,autocomplete='email',autocomplete='off' everywhere,Medium
59,Forms,Required Indicators,All,Mark required fields clearly,Use asterisk or (required) text,No indication of required fields,* required indicator,Guess which are required,Medium
60,Forms,Password Visibility,All,Let users see password while typing,Toggle to show/hide password,No visibility toggle,Show/hide password button,Password always hidden,Medium
61,Forms,Submit Feedback,All,Confirm form submission status,Show loading then success/error state,No feedback after submit,Loading -> Success message,Button click with no response,High
62,Forms,Input Affordance,All,Inputs should look interactive,Use distinct input styling,Inputs that look like plain text,Border/background on inputs,Borderless inputs,Medium
63,Forms,Mobile Keyboards,Mobile,Show appropriate keyboard for input type,Use inputmode attribute,Default keyboard for all inputs,inputmode='numeric',Text keyboard for numbers,Medium
64,Responsive,Mobile First,Web,Design for mobile then enhance for larger,Start with mobile styles then add breakpoints,Desktop-first causing mobile issues,Default mobile + md: lg: xl:,Desktop default + max-width queries,Medium
65,Responsive,Breakpoint Testing,Web,Test at all common screen sizes,Test at 320 375 414 768 1024 1440,Only test on your device,Multiple device testing,Single device development,Medium
66,Responsive,Touch Friendly,Web,Mobile layouts need touch-sized targets,Increase touch targets on mobile,Same tiny buttons on mobile,Larger buttons on mobile,Desktop-sized targets on mobile,High
67,Responsive,Readable Font Size,All,Text must be readable on all devices,Minimum 16px body text on mobile,Tiny text on mobile,text-base or larger,text-xs for body text,High
68,Responsive,Viewport Meta,Web,Set viewport for mobile devices,Use width=device-width initial-scale=1,Missing or incorrect viewport,<meta name='viewport'...>,No viewport meta tag,High
69,Responsive,Horizontal Scroll,Web,Avoid horizontal scrolling,Ensure content fits viewport width,Content wider than viewport,max-w-full overflow-x-hidden,Horizontal scrollbar on mobile,High
70,Responsive,Image Scaling,Web,Images should scale with container,Use max-width: 100% on images,Fixed width images overflow,max-w-full h-auto,width='800' fixed,Medium
71,Responsive,Table Handling,Web,Tables can overflow on mobile,Use horizontal scroll or card layout,Wide tables breaking layout,overflow-x-auto wrapper,Table overflows viewport,Medium
72,Typography,Line Height,All,Adequate line height improves readability,Use 1.5-1.75 for body text,Cramped or excessive line height,leading-relaxed (1.625),leading-none (1),Medium
73,Typography,Line Length,Web,Long lines are hard to read,Limit to 65-75 characters per line,Full-width text on large screens,max-w-prose,Full viewport width text,Medium
74,Typography,Font Size Scale,All,Consistent type hierarchy aids scanning,Use consistent modular scale,Random font sizes,Type scale (12 14 16 18 24 32),Arbitrary sizes,Medium
75,Typography,Font Loading,Web,Fonts should load without layout shift,Reserve space with fallback font,Layout shift when fonts load,font-display: swap + similar fallback,No fallback font,Medium
76,Typography,Contrast Readability,All,Body text needs good contrast,Use darker text on light backgrounds,Gray text on gray background,text-gray-900 on white,text-gray-400 on gray-100,High
77,Typography,Heading Clarity,All,Headings should stand out from body,Clear size/weight difference,Headings similar to body text,Bold + larger size,Same size as body,Medium
78,Feedback,Loading Indicators,All,Loading feedback should match the expected wait and avoid flashing for near-instant work,Follow platform and component guidance; preserve layout focus and accessible busy status,Apply one timing threshold to every operation or leave long waits unexplained,Stable skeleton or progress with aria-busy,Flickering spinner or frozen UI,High
79,Feedback,Empty States,All,Guide users when no content exists,Show helpful message and action,Blank empty screens,No items yet. Create one!,Empty white space,Medium
80,Feedback,Error Recovery,All,Help users recover from errors,Provide clear next steps,Error without recovery path,Try again button + help link,Error message only,Medium
81,Feedback,Progress Indicators,All,Show progress for multi-step processes,Step indicators or progress bar,No indication of progress,Step 2 of 4 indicator,No step information,Medium
82,Feedback,Toast Notifications,All,Transient messages for non-critical info,Auto-dismiss after 3-5 seconds,Toasts that never disappear,Auto-dismiss toast,Persistent toast,Medium
83,Feedback,Confirmation Messages,All,Confirm successful actions,Brief success message,Silent success,Saved successfully toast,No confirmation,Medium
84,Content,Truncation,All,Handle long content gracefully,Truncate with ellipsis and expand option,Overflow or broken layout,line-clamp-2 with expand,Overflow or cut off,Medium
85,Content,Date Formatting,All,Use locale-appropriate date formats,Use relative or locale-aware dates,Ambiguous date formats,2 hours ago or locale format,01/02/03,Low
86,Content,Number Formatting,All,Format large numbers for readability,Use thousand separators or abbreviations,Long unformatted numbers,"1.2K or 1,234",1234567,Low
87,Content,Placeholder Content,All,Show realistic placeholders during dev,Use realistic sample data,Lorem ipsum everywhere,Real sample content,Lorem ipsum,Low
88,Onboarding,User Freedom,All,Users should be able to skip tutorials,Provide Skip and Back buttons,Force linear unskippable tour,Skip Tutorial button,Locked overlay until finished,Medium
89,Search,Autocomplete,Web,Help users find results faster,Show predictions as user types,Require full type and enter,Debounced fetch + dropdown,No suggestions,Medium
90,Search,No Results,Web,Dead ends frustrate users,Show 'No results' with suggestions,Blank screen or '0 results',Try searching for X instead,No results found.,Medium
91,Data Entry,Bulk Actions,Web,Editing one by one is tedious,Allow multi-select and bulk edit,Single row actions only,Checkbox column + Action bar,Repeated actions per row,Low
92,AI Interaction,Disclaimer,All,Users need to know they talk to AI,Clearly label AI generated content,Present AI as human,AI Assistant label,Fake human name without label,High
93,AI Interaction,Streaming,All,Waiting for full text is slow,Stream text response token by token,Show loading spinner for 10s+,Typewriter effect,Spinner until 100% complete,Medium
94,Spatial UI,Gaze Hover,VisionOS,Elements should respond to eye tracking before pinch,Scale/highlight element on look,Static element until pinch,hoverEffect(),onTap only,High
