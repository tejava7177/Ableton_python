#pragma once

#include <juce_gui_extra/juce_gui_extra.h>

class BackingSummaryComponent final : public juce::Component
{
public:
    BackingSummaryComponent();

    void paint(juce::Graphics& g) override;
    void resized() override;

    void setSummary(const juce::String& styleSectionText,
                    const juce::String& drumsText,
                    const juce::String& bassText,
                    const juce::String& feelText,
                    const juce::String& helperText);

private:
    juce::Label titleLabel;
    juce::Label subtitleLabel;
    juce::Label styleSectionLabel;
    juce::Label drumsLabel;
    juce::Label bassLabel;
    juce::Label feelLabel;
    juce::Label helperLabel;

    void configureInfoLabel(juce::Label& label);
    void drawInfoCard(juce::Graphics& g, juce::Rectangle<int> bounds) const;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(BackingSummaryComponent)
};
