#pragma once

#include <juce_gui_extra/juce_gui_extra.h>

class TransportComponent final : public juce::Component
{
public:
    TransportComponent();

    void paint(juce::Graphics& g) override;
    void resized() override;

private:
    juce::Label titleLabel;
    juce::Label statusLabel;
    juce::TextButton playButton { "Play" };
    juce::TextButton stopButton { "Stop" };

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(TransportComponent)
};
