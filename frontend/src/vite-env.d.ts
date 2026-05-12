/// <reference types="vite/client" />

declare const __API_BASE_URL__: string | undefined;

declare const process: {
  env: {
    VITE_API_BASE_URL?: string;
  };
};
