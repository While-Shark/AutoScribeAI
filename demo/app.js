const samples = {
  "uptime-kuma": {
    title: "Uptime Kuma · 简体中文",
    html: "/manuals/uptime-kuma/index.html",
    docx: "/manuals/uptime-kuma/manual.docx"
  },
  "changedetection": {
    title: "changedetection.io · 日本語",
    html: "/manuals/changedetection/index.html",
    docx: "/manuals/changedetection/manual.docx"
  },
  "it-tools": {
    title: "IT Tools · 한국어",
    html: "/manuals/it-tools/index.html",
    docx: "/manuals/it-tools/manual.docx"
  }
};

const catalog = {
  en: {
    pageTitle: "AutoScribeAI Demo Gallery",
    metaDescription: "AutoScribeAI demo gallery: real software workflows turned into evidence-backed HTML, Word and Markdown manuals.",
    skipToExamples: "Skip to examples",
    navExamples: "Examples",
    navHow: "How it works",
    languageLabel: "Language",
    heroEyebrow: "Evidence-backed software manuals",
    heroTitle: "Give AI a project.<br>Get a manual people can actually follow.",
    heroCopy: "AutoScribeAI turns real, authorized software usage into illustrated documentation. It keeps screenshots, workflow evidence, verification status and exportable deliverables together—without requiring a hosted AutoScribeAI backend.",
    heroPrimary: "Explore real outputs",
    heroSecondary: "View source",
    trustAria: "Key capabilities",
    trustScreenshots: "Real screenshots",
    flowAria: "AutoScribeAI output flow",
    flowAnalyze: "Analyze",
    flowAnalyzeDesc: "Modules, features, roles, candidate workflows",
    flowExplore: "Explore",
    flowExploreDesc: "Operate the UI and capture real evidence",
    flowVerify: "Verify",
    flowVerifyDesc: "Keep observed results separate from inference",
    flowDeliver: "Deliver",
    flowDeliverDesc: "HTML, Word, Markdown and coverage reports",
    signalProjects: "real project examples",
    signalLanguages: "built-in output languages",
    signalFormats: "delivery formats",
    signalServers: "AutoScribeAI servers to deploy",
    examplesEyebrow: "Real outputs",
    examplesTitle: "See what the generated manuals look like",
    examplesCopy: "These are not mockups. Each example keeps its actual screenshots, structured manual, coverage status and export files. Unverified workflows stay visibly unverified.",
    uptimeAria: "Open Uptime Kuma manual preview",
    uptimeStatus: "3 / 3 verified",
    uptimeTitle: "Monitor, notification and public status page",
    uptimeCopy: "All three target workflows were exercised in a temporary demo instance with real screenshots. Webhook delivery itself was intentionally not tested.",
    changedetectionAria: "Open changedetection.io manual preview",
    changedetectionStatus: "0 / 3 verified",
    changedetectionTitle: "Honest documentation when exploration is blocked",
    changedetectionCopy: "The public site was observed, but paid subscription gates prevented the target workflows from being validated. The manual records that limitation instead of inventing steps.",
    itToolsAria: "Open IT Tools manual preview",
    itToolsStatus: "1 / 3 verified",
    itToolsTitle: "Mixed verified and source-discovered workflows",
    itToolsCopy: "JSON → YAML was executed and verified. Hash and QR workflows remain source-derived candidates, so the output clearly separates observed evidence from planned coverage.",
    openManual: "Open manual",
    previewWord: "Preview Word",
    previewNote: "Word preview opens the actual generated <code>.docx</code> through Microsoft Office's public web viewer. A direct DOCX link is always available in the preview dialog.",
    whyEyebrow: "Why it is useful",
    whyTitle: "Documentation that stays tied to what really happened",
    feature1Title: "Evidence, not hallucinated clicks",
    feature1Copy: "Verified workflows require observed results and screenshot evidence. Source analysis can suggest coverage, but it cannot masquerade as a completed operation.",
    feature2Title: "One source, multiple deliverables",
    feature2Copy: "<code>manual.json</code> is the single source of truth. The same content renders to searchable HTML, editable DOCX and repository-friendly Markdown.",
    feature3Title: "Works with different AI hosts",
    feature3Copy: "The Skill Pack adapts to the browser, computer-use, terminal and file tools available in the host instead of depending on a dedicated AutoScribeAI service.",
    feature4Title: "Safe to stop and resume",
    feature4Copy: "File-based manifests and checkpoints preserve progress. Interrupted side-effecting actions are reviewed before continuing rather than blindly replayed.",
    calloutEyebrow: "Portable Skill Pack",
    calloutTitle: "No AutoScribeAI server required.",
    calloutCopy: "Keep the skills, schemas and scripts together, give them to an AI host, and point the AI at the project you want documented.",
    calloutButton: "Open AutoScribeAI on GitHub",
    footerTagline: "AutoScribeAI · evidence-backed visual manuals",
    manualPreview: "Manual preview",
    wordPreview: "Generated Word document",
    htmlPreview: "Interactive HTML manual",
    downloadDocx: "Download DOCX ↗",
    openFullPage: "Open full page ↗",
    loadingPreview: "Loading preview…",
    closePreview: "Close preview",
    previewFrameTitle: "Manual preview"
  },
  "zh-CN": {
    pageTitle: "AutoScribeAI 在线示例",
    metaDescription: "AutoScribeAI 在线示例：把真实软件操作生成带证据的 HTML、Word 和 Markdown 操作手册。",
    skipToExamples: "跳到示例",
    navExamples: "真实示例",
    navHow: "工作方式",
    languageLabel: "语言",
    heroEyebrow: "基于真实证据的软件操作手册",
    heroTitle: "把项目交给 AI。<br>得到一套真正能照着使用的操作手册。",
    heroCopy: "AutoScribeAI 把真实、已授权的软件操作变成图文文档，同时保留截图、流程证据、验证状态和可交付产物，而且不需要部署 AutoScribeAI 后端服务。",
    heroPrimary: "查看真实效果",
    heroSecondary: "查看源码",
    trustAria: "核心能力",
    trustScreenshots: "真实截图",
    flowAria: "AutoScribeAI 输出流程",
    flowAnalyze: "分析",
    flowAnalyzeDesc: "模块、功能、角色、候选流程",
    flowExplore: "探索",
    flowExploreDesc: "真实操作界面并采集证据",
    flowVerify: "核验",
    flowVerifyDesc: "把真实观察与推断严格区分",
    flowDeliver: "交付",
    flowDeliverDesc: "HTML、Word、Markdown 和覆盖率报告",
    signalProjects: "个真实项目示例",
    signalLanguages: "种内置输出语言",
    signalFormats: "种交付格式",
    signalServers: "个需要部署的 AutoScribeAI 服务",
    examplesEyebrow: "真实产物",
    examplesTitle: "直接看看生成出来的手册是什么样",
    examplesCopy: "这些不是 UI Mockup。每个示例都保留真实截图、结构化手册、覆盖情况和导出文件；没有验证的流程会明确保持未验证。",
    uptimeAria: "打开 Uptime Kuma 手册预览",
    uptimeStatus: "3 / 3 已验证",
    uptimeTitle: "监控、通知配置与公开状态页",
    uptimeCopy: "三个目标流程都在临时 Demo 实例中实际操作并留下截图。Webhook 的真实消息投递没有执行，并在结果中明确保留该限制。",
    changedetectionAria: "打开 changedetection.io 手册预览",
    changedetectionStatus: "0 / 3 已验证",
    changedetectionTitle: "探索受阻时，也不编造操作步骤",
    changedetectionCopy: "实际访问了公开站点，但付费订阅流程阻止了目标功能验证。手册如实记录受阻原因，而不是根据猜测补步骤。",
    itToolsAria: "打开 IT Tools 手册预览",
    itToolsStatus: "1 / 3 已验证",
    itToolsTitle: "真实验证与源码发现的流程明确分开",
    itToolsCopy: "JSON → YAML 已实际操作并验证。文本哈希和 QR 码仍是源码发现的候选流程，因此输出会明确区分已观察证据与计划覆盖。",
    openManual: "打开手册",
    previewWord: "预览 Word",
    previewNote: "Word 预览会通过 Microsoft Office 公共在线查看器打开实际生成的 <code>.docx</code>；预览窗口中始终保留直接打开 DOCX 的入口。",
    whyEyebrow: "为什么实用",
    whyTitle: "让操作手册始终和真实发生过的事情绑定",
    feature1Title: "有证据，不脑补点击过程",
    feature1Copy: "只有存在实际结果和截图证据的流程才能标记为已验证。源码分析可以发现候选功能，但不能伪装成已完成操作。",
    feature2Title: "一份数据，多种交付",
    feature2Copy: "<code>manual.json</code> 是唯一事实源，同一份内容生成可搜索 HTML、可编辑 DOCX 和适合仓库的 Markdown。",
    feature3Title: "适配不同 AI Agent",
    feature3Copy: "Skill Pack 会利用宿主已有的浏览器、Computer Use、终端和文件能力，而不是绑定到某一个专用 AutoScribeAI 服务。",
    feature4Title: "可以安全中断和继续",
    feature4Copy: "文件化 manifest 和 checkpoint 保存进度；被中断的有副作用操作会先核对状态，不会盲目重复执行。",
    calloutEyebrow: "便携 Skill Pack",
    calloutTitle: "不需要部署 AutoScribeAI 服务。",
    calloutCopy: "保留 skills、schemas 和 scripts，把完整目录交给 AI Agent，再告诉它需要生成手册的目标项目即可。",
    calloutButton: "在 GitHub 打开 AutoScribeAI",
    footerTagline: "AutoScribeAI · 有真实证据的图文操作手册",
    manualPreview: "手册预览",
    wordPreview: "生成的 Word 文档",
    htmlPreview: "交互式 HTML 手册",
    downloadDocx: "打开 DOCX ↗",
    openFullPage: "打开完整页面 ↗",
    loadingPreview: "正在加载预览…",
    closePreview: "关闭预览",
    previewFrameTitle: "手册预览"
  },
  ja: {
    pageTitle: "AutoScribeAI Demo Gallery",
    metaDescription: "AutoScribeAI のデモ：実際のソフトウェア操作から、証拠付き HTML・Word・Markdown マニュアルを生成します。",
    skipToExamples: "サンプルへ移動",
    navExamples: "サンプル",
    navHow: "仕組み",
    languageLabel: "言語",
    heroEyebrow: "実証拠に基づくソフトウェアマニュアル",
    heroTitle: "AI にプロジェクトを渡す。<br>実際に使える操作マニュアルを得る。",
    heroCopy: "AutoScribeAI は、許可された実際のソフトウェア操作を画像付きドキュメントに変換し、スクリーンショット、ワークフロー証拠、検証状態、出力物を一緒に保持します。専用バックエンドは不要です。",
    heroPrimary: "実際の出力を見る",
    heroSecondary: "ソースを見る",
    trustAria: "主な機能",
    trustScreenshots: "実スクリーンショット",
    flowAria: "AutoScribeAI 出力フロー",
    flowAnalyze: "分析",
    flowAnalyzeDesc: "モジュール、機能、ロール、候補ワークフロー",
    flowExplore: "探索",
    flowExploreDesc: "UI を実操作して証拠を収集",
    flowVerify: "検証",
    flowVerifyDesc: "実観察と推論を明確に分離",
    flowDeliver: "出力",
    flowDeliverDesc: "HTML、Word、Markdown、カバレッジレポート",
    signalProjects: "件の実プロジェクト例",
    signalLanguages: "言語の内蔵出力",
    signalFormats: "種類の出力形式",
    signalServers: "台の専用 AutoScribeAI サーバー",
    examplesEyebrow: "実際の出力",
    examplesTitle: "生成されたマニュアルをそのまま確認",
    examplesCopy: "これらはモックアップではありません。各サンプルには実スクリーンショット、構造化マニュアル、カバレッジ状態、エクスポートファイルが含まれます。未検証のフローは未検証のまま表示されます。",
    uptimeAria: "Uptime Kuma マニュアルを開く",
    uptimeStatus: "3 / 3 検証済み",
    uptimeTitle: "監視、通知設定、公開ステータスページ",
    uptimeCopy: "3 つの対象ワークフローを一時デモ環境で実行し、実スクリーンショットを取得しました。Webhook の実配信は意図的にテストしていません。",
    changedetectionAria: "changedetection.io マニュアルを開く",
    changedetectionStatus: "0 / 3 検証済み",
    changedetectionTitle: "探索できない場合も手順を捏造しない",
    changedetectionCopy: "公開サイトは確認しましたが、有料サブスクリプション導線により対象フローを検証できませんでした。マニュアルは制約をそのまま記録します。",
    itToolsAria: "IT Tools マニュアルを開く",
    itToolsStatus: "1 / 3 検証済み",
    itToolsTitle: "実測フローとソース由来候補を明確に分離",
    itToolsCopy: "JSON → YAML は実行・検証済みです。ハッシュと QR コードはソースから見つけた候補のままで、観察済み証拠と計画カバレッジを分けています。",
    openManual: "マニュアルを開く",
    previewWord: "Word をプレビュー",
    previewNote: "Word プレビューは Microsoft Office の公開 Web Viewer で実際に生成された <code>.docx</code> を開きます。プレビュー内には DOCX を直接開くリンクもあります。",
    whyEyebrow: "実用的な理由",
    whyTitle: "実際に起きたこととマニュアルを結びつける",
    feature1Title: "推測ではなく証拠",
    feature1Copy: "verified にするには実結果とスクリーンショット証拠が必要です。ソース解析は候補を提案できますが、完了操作として扱いません。",
    feature2Title: "1 つのデータから複数の成果物",
    feature2Copy: "<code>manual.json</code> が単一の事実源です。同じ内容から検索可能 HTML、編集可能 DOCX、リポジトリ向け Markdown を生成します。",
    feature3Title: "さまざまな AI Agent に対応",
    feature3Copy: "専用サービスに依存せず、ホストが持つブラウザ、Computer Use、ターミナル、ファイル機能を利用します。",
    feature4Title: "安全に中断・再開",
    feature4Copy: "ファイルベースの manifest と checkpoint で進捗を保存し、中断した副作用操作は状態確認後に再開します。",
    calloutEyebrow: "ポータブル Skill Pack",
    calloutTitle: "AutoScribeAI サーバーは不要です。",
    calloutCopy: "skills、schemas、scripts を一緒に保ち、AI Agent に渡して、文書化したいプロジェクトを指定するだけです。",
    calloutButton: "GitHub で AutoScribeAI を開く",
    footerTagline: "AutoScribeAI · 証拠付きビジュアルマニュアル",
    manualPreview: "マニュアルプレビュー",
    wordPreview: "生成済み Word 文書",
    htmlPreview: "インタラクティブ HTML マニュアル",
    downloadDocx: "DOCX を開く ↗",
    openFullPage: "完全なページを開く ↗",
    loadingPreview: "プレビューを読み込み中…",
    closePreview: "プレビューを閉じる",
    previewFrameTitle: "マニュアルプレビュー"
  },
  ko: {
    pageTitle: "AutoScribeAI Demo Gallery",
    metaDescription: "AutoScribeAI 데모: 실제 소프트웨어 사용 흐름을 증거 기반 HTML, Word, Markdown 매뉴얼로 변환합니다.",
    skipToExamples: "예제로 이동",
    navExamples: "예제",
    navHow: "작동 방식",
    languageLabel: "언어",
    heroEyebrow: "실제 증거 기반 소프트웨어 매뉴얼",
    heroTitle: "프로젝트를 AI에 전달하세요.<br>실제로 따라 할 수 있는 매뉴얼을 받으세요.",
    heroCopy: "AutoScribeAI는 승인된 실제 소프트웨어 사용 과정을 이미지 문서로 바꾸고 스크린샷, 워크플로 증거, 검증 상태, 결과물을 함께 보존합니다. 별도 AutoScribeAI 백엔드는 필요하지 않습니다.",
    heroPrimary: "실제 결과 보기",
    heroSecondary: "소스 보기",
    trustAria: "핵심 기능",
    trustScreenshots: "실제 스크린샷",
    flowAria: "AutoScribeAI 출력 흐름",
    flowAnalyze: "분석",
    flowAnalyzeDesc: "모듈, 기능, 역할, 후보 워크플로",
    flowExplore: "탐색",
    flowExploreDesc: "UI를 실제 조작하고 증거 수집",
    flowVerify: "검증",
    flowVerifyDesc: "실제 관찰과 추론을 명확히 분리",
    flowDeliver: "결과물",
    flowDeliverDesc: "HTML, Word, Markdown, 커버리지 보고서",
    signalProjects: "개의 실제 프로젝트 예제",
    signalLanguages: "개의 내장 출력 언어",
    signalFormats: "개의 전달 형식",
    signalServers: "개의 별도 AutoScribeAI 서버",
    examplesEyebrow: "실제 결과물",
    examplesTitle: "생성된 매뉴얼을 직접 확인하세요",
    examplesCopy: "이 화면은 목업이 아닙니다. 각 예제는 실제 스크린샷, 구조화 매뉴얼, 커버리지 상태, 내보내기 파일을 그대로 보존합니다. 검증하지 못한 흐름은 미검증 상태로 남습니다.",
    uptimeAria: "Uptime Kuma 매뉴얼 미리보기 열기",
    uptimeStatus: "3 / 3 검증 완료",
    uptimeTitle: "모니터, 알림 설정, 공개 상태 페이지",
    uptimeCopy: "세 가지 대상 워크플로를 임시 데모 환경에서 실제 실행하고 스크린샷을 수집했습니다. Webhook 실제 전송은 의도적으로 테스트하지 않았습니다.",
    changedetectionAria: "changedetection.io 매뉴얼 미리보기 열기",
    changedetectionStatus: "0 / 3 검증 완료",
    changedetectionTitle: "탐색이 막혀도 절차를 만들어내지 않음",
    changedetectionCopy: "공개 사이트는 실제로 확인했지만 유료 구독 흐름 때문에 대상 기능을 검증할 수 없었습니다. 매뉴얼은 제약을 그대로 기록합니다.",
    itToolsAria: "IT Tools 매뉴얼 미리보기 열기",
    itToolsStatus: "1 / 3 검증 완료",
    itToolsTitle: "실제 검증과 소스 기반 후보 흐름을 분리",
    itToolsCopy: "JSON → YAML은 실제 실행하고 검증했습니다. 해시와 QR 코드는 소스에서 찾은 후보 흐름으로 남아 있어 관찰 증거와 계획 커버리지를 명확히 구분합니다.",
    openManual: "매뉴얼 열기",
    previewWord: "Word 미리보기",
    previewNote: "Word 미리보기는 Microsoft Office 공개 웹 뷰어를 통해 실제 생성된 <code>.docx</code>를 엽니다. 미리보기 창에서 DOCX를 직접 열 수도 있습니다.",
    whyEyebrow: "왜 실용적인가",
    whyTitle: "실제로 일어난 일과 문서를 연결",
    feature1Title: "추측 클릭이 아닌 증거",
    feature1Copy: "verified 상태에는 실제 결과와 스크린샷 증거가 필요합니다. 소스 분석은 후보를 찾을 수 있지만 완료된 작업처럼 표시하지 않습니다.",
    feature2Title: "하나의 데이터, 여러 결과물",
    feature2Copy: "<code>manual.json</code>이 단일 기준 데이터입니다. 같은 내용에서 검색 가능한 HTML, 편집 가능한 DOCX, 저장소 친화적 Markdown을 생성합니다.",
    feature3Title: "다양한 AI Agent에 대응",
    feature3Copy: "전용 AutoScribeAI 서비스에 의존하지 않고 호스트의 브라우저, Computer Use, 터미널, 파일 기능을 활용합니다.",
    feature4Title: "안전하게 중단하고 재개",
    feature4Copy: "파일 기반 manifest와 checkpoint가 진행 상태를 저장하며, 중단된 변경 작업은 상태를 확인한 뒤 다시 진행합니다.",
    calloutEyebrow: "휴대형 Skill Pack",
    calloutTitle: "AutoScribeAI 서버가 필요 없습니다.",
    calloutCopy: "skills, schemas, scripts를 함께 보관하고 AI Agent에 전달한 뒤 문서화할 프로젝트를 지정하면 됩니다.",
    calloutButton: "GitHub에서 AutoScribeAI 열기",
    footerTagline: "AutoScribeAI · 실제 증거 기반 비주얼 매뉴얼",
    manualPreview: "매뉴얼 미리보기",
    wordPreview: "생성된 Word 문서",
    htmlPreview: "인터랙티브 HTML 매뉴얼",
    downloadDocx: "DOCX 열기 ↗",
    openFullPage: "전체 페이지 열기 ↗",
    loadingPreview: "미리보기를 불러오는 중…",
    closePreview: "미리보기 닫기",
    previewFrameTitle: "매뉴얼 미리보기"
  }
};

const supportedLanguages = ["en", "zh-CN", "ja", "ko"];
const storageKey = "autoscribe-demo-language";

const dialog = document.querySelector("#preview-dialog");
const frame = document.querySelector("#preview-frame");
const title = document.querySelector("#preview-title");
const kind = document.querySelector("#preview-kind");
const direct = document.querySelector("#preview-direct");
const close = document.querySelector("#preview-close");
const loading = document.querySelector("#preview-loading");
const languageSelector = document.querySelector("#language-selector");
const metaDescription = document.querySelector("#meta-description");

let currentLanguage = "en";

function normalizeLanguage(value) {
  if (!value) return null;
  const lower = value.toLowerCase();
  if (lower.startsWith("zh")) return "zh-CN";
  if (lower.startsWith("ja")) return "ja";
  if (lower.startsWith("ko")) return "ko";
  if (lower.startsWith("en")) return "en";
  return null;
}

function resolveInitialLanguage() {
  const params = new URLSearchParams(window.location.search);
  const fromUrl = normalizeLanguage(params.get("lang"));
  if (fromUrl) return fromUrl;

  const fromStorage = normalizeLanguage(localStorage.getItem(storageKey));
  if (fromStorage) return fromStorage;

  return normalizeLanguage(navigator.language) || "en";
}

function t(key) {
  return catalog[currentLanguage]?.[key] ?? catalog.en[key] ?? key;
}

function applyLanguage(language, options = {}) {
  currentLanguage = supportedLanguages.includes(language) ? language : "en";
  const locale = catalog[currentLanguage];

  document.documentElement.lang = currentLanguage;
  document.title = locale.pageTitle;
  metaDescription.setAttribute("content", locale.metaDescription);
  languageSelector.value = currentLanguage;

  document.querySelectorAll("[data-i18n]").forEach((element) => {
    const value = locale[element.dataset.i18n] ?? catalog.en[element.dataset.i18n];
    if (value != null) element.textContent = value;
  });

  document.querySelectorAll("[data-i18n-html]").forEach((element) => {
    const value = locale[element.dataset.i18nHtml] ?? catalog.en[element.dataset.i18nHtml];
    if (value != null) element.innerHTML = value;
  });

  document.querySelectorAll("[data-i18n-aria]").forEach((element) => {
    const value = locale[element.dataset.i18nAria] ?? catalog.en[element.dataset.i18nAria];
    if (value != null) element.setAttribute("aria-label", value);
  });

  document.querySelectorAll("[data-i18n-title]").forEach((element) => {
    const value = locale[element.dataset.i18nTitle] ?? catalog.en[element.dataset.i18nTitle];
    if (value != null) element.setAttribute("title", value);
  });

  if (options.persist !== false) {
    localStorage.setItem(storageKey, currentLanguage);
  }

  if (options.syncUrl !== false) {
    const url = new URL(window.location.href);
    if (currentLanguage === "en") {
      url.searchParams.delete("lang");
    } else {
      url.searchParams.set("lang", currentLanguage);
    }
    history.replaceState(null, "", url);
  }

  refreshOpenPreviewLabels();
}

function absoluteUrl(path) {
  return new URL(path, window.location.origin).href;
}

function refreshOpenPreviewLabels() {
  if (!dialog.open) return;
  const previewType = dialog.dataset.previewType;
  if (previewType === "word") {
    kind.textContent = t("wordPreview");
    direct.textContent = t("downloadDocx");
  } else {
    kind.textContent = t("htmlPreview");
    direct.textContent = t("openFullPage");
  }
  loading.textContent = t("loadingPreview");
}

function openPreview(sampleKey, type) {
  const sample = samples[sampleKey];
  if (!sample) return;

  dialog.dataset.previewType = type;
  title.textContent = sample.title;
  loading.hidden = false;
  loading.textContent = t("loadingPreview");

  if (type === "word") {
    const fileUrl = absoluteUrl(sample.docx);
    const viewerUrl = "https://view.officeapps.live.com/op/embed.aspx?src=" + encodeURIComponent(fileUrl);
    kind.textContent = t("wordPreview");
    direct.textContent = t("downloadDocx");
    direct.href = sample.docx;
    frame.src = viewerUrl;
  } else {
    kind.textContent = t("htmlPreview");
    direct.textContent = t("openFullPage");
    direct.href = sample.html;
    frame.src = sample.html;
  }

  dialog.showModal();
}

languageSelector.addEventListener("change", (event) => {
  applyLanguage(event.target.value);
});

document.addEventListener("click", (event) => {
  const target = event.target.closest("[data-preview]");
  if (!target) return;
  openPreview(target.dataset.sample, target.dataset.preview);
});

frame.addEventListener("load", () => {
  loading.hidden = true;
});

close.addEventListener("click", () => {
  dialog.close();
});

dialog.addEventListener("click", (event) => {
  if (event.target === dialog) dialog.close();
});

dialog.addEventListener("close", () => {
  frame.src = "about:blank";
  direct.href = "#";
  delete dialog.dataset.previewType;
  loading.hidden = true;
});

applyLanguage(resolveInitialLanguage(), { persist: false });
