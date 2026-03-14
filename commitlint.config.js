// commitlint.config.js — Convention de commit (ADR-003, ADR-020)
// Tout commit doit suivre Conventional Commits.
// La référence ADR (ex: "Référence : ADR-001") est requise dans le corps du message.
export default {
  extends: ['@commitlint/config-conventional'],
  rules: {
    // Types autorisés
    'type-enum': [
      2,
      'always',
      ['feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore', 'ci', 'perf', 'revert'],
    ],
    // Le sujet doit avoir entre 10 et 100 caractères
    'subject-max-length': [2, 'always', 100],
    'subject-min-length': [2, 'always', 10],
    // Pas de majuscule en début (ex: "feat: Ajoute..." est refusé)
    'subject-case': [2, 'never', ['start-case', 'pascal-case', 'upper-case']],
    // Le corps du commit est obligatoire (pour y inclure la référence ADR)
    'body-min-length': [2, 'always', 10],
    'body-max-line-length': [2, 'always', 120],
  },
};
