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

    const checkbox = wrapper.find('input[type="checkbox"]');
    await checkbox.setValue(true);
    expect(wrapper.emitted("update:enableDeepThinking")?.[0]).toEqual([true]);
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
});
