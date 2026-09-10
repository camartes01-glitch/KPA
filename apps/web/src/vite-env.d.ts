/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL?: string;
  readonly VITE_GOOGLE_CLIENT_ID?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

declare namespace google {
  namespace accounts {
    namespace id {
      interface CredentialResponse {
        credential: string;
        select_by?: string;
        clientId?: string;
      }

      interface GsiButtonConfiguration {
        type?: "standard" | "icon";
        theme?: "outline" | "filled_blue" | "filled_black";
        size?: "large" | "medium" | "small";
        text?: "signin_with" | "signup_with" | "continue_with" | "signin";
        shape?: "rectangular" | "pill" | "circle" | "square";
        logo_alignment?: "left" | "center";
        width?: string | number;
        locale?: string;
      }

      interface IdConfiguration {
        client_id: string;
        callback: (response: CredentialResponse) => void;
        auto_select?: boolean;
        cancel_on_tap_outside?: boolean;
        context?: "signin" | "signup" | "use";
      }

      function initialize(config: IdConfiguration): void;
      function renderButton(parent: HTMLElement, options: GsiButtonConfiguration): void;
      function prompt(momentListener?: (moment: any) => void): void;
      function disableAutoSelect(): void;
    }
  }
}
