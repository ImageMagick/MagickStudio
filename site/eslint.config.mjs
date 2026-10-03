import { defineConfig } from 'eslint/config'
import pluginTypescriptEslint from '@typescript-eslint/eslint-plugin'
import tsParser from '@typescript-eslint/parser'

export default defineConfig([{
    files: [
        '**/*.ts',
    ],

    ignores: [
        'dist/*',
    ],

    plugins: {
        '@typescript-eslint': pluginTypescriptEslint,
    },

    extends: [
        '@typescript-eslint/eslint-recommended',
        '@typescript-eslint/recommended',
    ],

    languageOptions: {
        parser: tsParser,

        parserOptions: {
            project: [
                './tsconfig.app.json',
                './tsconfig.node.json',
            ],
        },
    },
}])
