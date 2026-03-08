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
    expect(wrapper.emitted("send")?.[0]).toEqual(["hello"]);
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

    const toggle = wrapper.find("button.settings-btn");
    await toggle.trigger("click");
    const keyInput = wrapper.find('[data-testid="api-key-input"]');
    await keyInput.setValue("sk-demo");
    expect(wrapper.emitted("update:userApiKey")?.[0]).toEqual(["sk-demo"]);
  });
});
