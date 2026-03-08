import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import ChatInput from "./ChatInput.vue";

describe("ChatInput", () => {
  it("emits send on Enter", async () => {
    const wrapper = mount(ChatInput, {
      props: {
        isStreaming: false,
        disabled: false,
        enableDeepThinking: false
      }
    });

    const textarea = wrapper.find("textarea");
    await textarea.setValue("hello");
    await textarea.trigger("keydown", { key: "Enter", shiftKey: false });

    expect(wrapper.emitted("send")).toHaveLength(1);
    expect(wrapper.emitted("send")?.[0]).toEqual([{ content: "hello", attachments: [] }]);
  });

  it("does not emit send on Shift+Enter", async () => {
    const wrapper = mount(ChatInput, {
      props: {
        isStreaming: false,
        disabled: false,
        enableDeepThinking: false
      }
    });

    const textarea = wrapper.find("textarea");
    await textarea.setValue("hello");
    await textarea.trigger("keydown", { key: "Enter", shiftKey: true });

    expect(wrapper.emitted("send")).toBeUndefined();
  });

  it("emits deep thinking toggle update", async () => {
    const wrapper = mount(ChatInput, {
      props: {
        isStreaming: false,
        disabled: false,
        enableDeepThinking: false
      }
    });

    const checkbox = wrapper.find('[data-testid="deep-thinking-toggle"]');
    await checkbox.setValue(true);
    expect(wrapper.emitted("update:enableDeepThinking")?.[0]).toEqual([true]);
  });

  it("emits web search toggle update", async () => {
    const wrapper = mount(ChatInput, {
      props: {
        isStreaming: false,
        disabled: false,
        enableDeepThinking: false,
        enableWebSearch: false
      }
    });

    const checkbox = wrapper.find('[data-testid="web-search-toggle"]');
    await checkbox.setValue(true);
    expect(wrapper.emitted("update:enableWebSearch")?.[0]).toEqual([true]);
  });

  it("emits stop when primary button clicked in streaming mode", async () => {
    const wrapper = mount(ChatInput, {
      props: {
        isStreaming: true,
        disabled: false,
        enableDeepThinking: false
      }
    });

    const button = wrapper.find("button.primary-btn");
    await button.trigger("click");
    expect(wrapper.emitted("stop")).toHaveLength(1);
  });

  it("emits user api key update in api settings", async () => {
    const wrapper = mount(ChatInput, {
      props: {
        isStreaming: false,
        disabled: false,
        enableDeepThinking: false,
        userApiKey: ""
      }
    });

    const toggle = wrapper.findAll("button.settings-btn").find((button) => button.text() === "API Settings");
    expect(toggle).toBeTruthy();
    await toggle!.trigger("click");
    const keyInput = wrapper.find('[data-testid="api-key-input"]');
    await keyInput.setValue("sk-demo");
    expect(wrapper.emitted("update:userApiKey")?.[0]).toEqual(["sk-demo"]);
  });

  it("includes text attachment in send payload", async () => {
    const OriginalFileReader = globalThis.FileReader;
    class MockFileReader {
      result: string | ArrayBuffer | null = null;
      onload: ((this: FileReader, ev: ProgressEvent<FileReader>) => unknown) | null = null;
      onerror: ((this: FileReader, ev: ProgressEvent<FileReader>) => unknown) | null = null;

      readAsText() {
        this.result = "from-file";
        if (this.onload) {
          this.onload.call(this as unknown as FileReader, new ProgressEvent("load"));
        }
      }
    }
    globalThis.FileReader = MockFileReader as unknown as typeof FileReader;
    try {
      const wrapper = mount(ChatInput, {
        props: {
          isStreaming: false,
          disabled: false,
          enableDeepThinking: false
        }
      });
      const file = new File(["from-file"], "note.txt", { type: "text/plain" });
      const input = wrapper.find('input[type="file"]');
      Object.defineProperty(input.element, "files", {
        value: [file],
        configurable: true
      });
      await input.trigger("change");
      await new Promise((resolve) => setTimeout(resolve, 0));
      const send = wrapper.find("button.primary-btn");
      await send.trigger("click");

      const payload = wrapper.emitted("send")?.[0]?.[0] as {
        content: string;
        attachments: Array<{ name: string }>;
      };
      expect(payload.attachments).toHaveLength(1);
      expect(payload.attachments[0].name).toBe("note.txt");
    } finally {
      globalThis.FileReader = OriginalFileReader;
    }
  });
});
