require(["gitbook"], (gitbook) => {
  // gitbook.state.root is the root of the current language book, and
  // gitbook.state.bookRoot the directory above it that holds every language.
  const switchTo = (lang) => {
    const page = location.pathname.slice(new URL(gitbook.state.root).pathname.length);
    const langRoot = new URL(`${lang}/`, gitbook.state.bookRoot);
    const target = new URL(page, langRoot);
    // Fall back to the top page when the page is not translated yet
    fetch(target, { method: "HEAD" })
      .then((res) => {
        location.href = res.ok ? target : langRoot;
      })
      .catch(() => {
        location.href = target;
      });
  };

  gitbook.events.bind("start", (_event, pluginsConfig) => {
    const { languages = [] } = pluginsConfig["lang-switch"] || {};
    const current = gitbook.state.innerLanguage;
    if (!current || languages.length < 2) {
      return;
    }
    gitbook.toolbar.createButton({
      icon: "fa fa-globe",
      label: "Language",
      position: "right",
      className: "lang-switch",
      dropdown: languages.map((lang) => ({
        text: lang.title,
        className: lang.id === current ? "lang-switch-current" : "",
        onClick: (event) => {
          event.preventDefault();
          if (lang.id !== current) {
            switchTo(lang.id);
          }
        },
      })),
    });
  });
});
