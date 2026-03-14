import js from '@eslint/js';
import ts from 'typescript-eslint';
import svelte from 'eslint-plugin-svelte';
import svelteParser from 'svelte-eslint-parser';
import globals from 'globals';

export default [
  js.configs.recommended,
  ...ts.configs.recommended,
  ...svelte.configs['flat/recommended'],
  {
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
      },
    },
  },
  {
    files: ['**/*.svelte'],
    languageOptions: {
      parser: svelteParser,
      parserOptions: {
        parser: ts.parser,
      },
    },
  },
  {
    rules: {
      // Interdit les variables non utilisées
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      // Interdit console.log en production
      'no-console': ['warn', { allow: ['warn', 'error'] }],
      // Force typage explicite des fonctions publiques
      '@typescript-eslint/explicit-function-return-type': 'warn',
    },
  },
  {
    ignores: ['node_modules/', '.svelte-kit/', 'build/', 'dist/', 'src-tauri/target/'],
  },
];
