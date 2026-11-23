require(["gitbook"], (gitbook) => {
  const LABELS = {
    ja: "ハンドブック一覧",
    en: "All handbooks",
  };

  gitbook.events.bind("start", () => {
    // gitbook.state.bookRoot is the handbook (<site>/<book>/), so the list of
    // handbooks is the directory above it.
    const label = LABELS[gitbook.state.innerLanguage] || LABELS.en;
    gitbook.toolbar.createButton({
      icon: "fa fa-th-large",
      label,
      position: "left",
      className: "handbooks-home",
      onClick: (event) => {
        event.preventDefault();
        location.href = new URL("../", gitbook.state.bookRoot);
      },
    });
  });
});
