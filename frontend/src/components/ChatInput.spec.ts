import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import ChatInput from "./ChatInput.vue";

describe("ChatInput", () => {
  it("emits send on Enter", async () => {
    const wrapper = mount(ChatInput, {
      props: {
        isStreaming: false,
        disabled: false
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
        disabled: false
      }
    });

    const textarea = wrapper.find("textarea");
    await textarea.setValue("hello");
    await textarea.trigger("keydown", { key: "Enter", shiftKey: true });

    expect(wrapper.emitted("send")).toBeUndefined();
  });
});
