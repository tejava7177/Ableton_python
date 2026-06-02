#pragma once

#include <functional>

#include <juce_gui_extra/juce_gui_extra.h>

class TransportComponent final : public juce::Component
{
public:
    TransportComponent();

    void paint(juce::Graphics& g) override;
    void resized() override;

    [[nodiscard]] juce::String getStatusText() const;
    [[nodiscard]] bool isLoopEnabled() const noexcept;
    void setOnGenerate(std::function<void()> callback);
    void setOnPlay(std::function<void()> callback);
    void setOnStop(std::function<void()> callback);
    void setStatusText(const juce::String& newStatus);

private:
    juce::Label titleLabel;
    juce::Label statusLabel;
    juce::TextButton generateButton { "Generate Backing" };
    juce::TextButton playButton { "Play" };
    juce::TextButton stopButton { "Stop" };
    juce::ToggleButton loopButton { "Loop" };
    std::function<void()> onGenerate;
    std::function<void()> onPlay;
    std::function<void()> onStop;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(TransportComponent)
};
