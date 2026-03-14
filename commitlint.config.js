// commitlint.config.js — Convention de commit (ADR 003, ADR 020)
// Tout commit doit suivre Conventional Commits ET citer un ADR
export default {
  extends: ['@commitlint/config-conventional'],
  rules: {
    // Types autorisés
    'type-enum': [
      2,
      'always',
      ['feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore', 'ci', 'perf', 'revert'],
    ],
    // Longueur du sujet
    'subject-max-length': [2, 'always', 100],
    'subject-min-length': [2, 'always', 10],
    // Langue : pas de majuscule en début de sujet
    'subject-case': [2, 'never', ['start-case', 'pascal-case', 'upper-case']],
    // Corps du message : référence ADR obligatoire
    // Format : "ADR-001" ou "ADR-013" dans le corps ou le pied de page
    'body-max-line-length': [2, 'always', 120],
  },
  // Plugin custom pour vérifier la référence ADR
  plugins: [
    {
      rules: {
        'adr-reference': ({ raw }) => {
          const hasAdrRef = /ADR-\d{3}/i.test(raw);
          return [
            hasAdrRef,
            'Le message de commit doit référencer un ADR (ex: ADR-001). Voir Documentation/adr/README.md',
          ];
        },
      },
    },
  ],
};
