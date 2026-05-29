#pragma once

#include <juce_gui_extra/juce_gui_extra.h>

class SectionPanelComponent final : public juce::Component
{
public:
    SectionPanelComponent();

    void paint(juce::Graphics& g) override;
    void resized() override;

private:
    juce::Label titleLabel;
    juce::TextButton mainAButton { "Main A" };
    juce::TextButton fillButton { "Fill" };
    juce::TextButton endingButton { "Ending" };

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(SectionPanelComponent)
};
