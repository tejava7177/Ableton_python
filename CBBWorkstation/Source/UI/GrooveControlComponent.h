#pragma once

#include <juce_gui_extra/juce_gui_extra.h>

class GrooveControlComponent final : public juce::Component
{
public:
    GrooveControlComponent();

    void paint(juce::Graphics& g) override;
    void resized() override;

private:
    juce::Label titleLabel;
    juce::Label energyLabel;
    juce::Label swingLabel;
    juce::Slider energySlider;
    juce::Slider swingSlider;

    void configureSlider(juce::Slider& slider);

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(GrooveControlComponent)
};
