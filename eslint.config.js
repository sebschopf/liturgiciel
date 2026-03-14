// eslint.config.js — ESLint pour TypeScript + Svelte 5 (ADR 003)
import js from '@eslint/js';
import ts from 'typescript-eslint';
import svelte from 'eslint-plugin-svelte';
import svelteParser from 'svelte-eslint-parser';

export default [
  js.configs.recommended,
  ...ts.configs.recommended,
  ...svelte.configs['flat/recommended'],
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
