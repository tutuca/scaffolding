import { createTestingPinia } from "@pinia/testing";
import { vi } from "vitest";

import piniaPluginPersistedstate from "pinia-plugin-persistedstate";

createTestingPinia({
    createSpy: vi.fn,
    plugins: [piniaPluginPersistedstate],
});
