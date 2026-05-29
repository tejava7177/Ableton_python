#pragma once

#include <juce_gui_extra/juce_gui_extra.h>

class ChordInputComponent final : public juce::Component
{
public:
    ChordInputComponent();

    void paint(juce::Graphics& g) override;
    void resized() override;

    [[nodiscard]] juce::String getChordText() const;

private:
    juce::Label titleLabel;
    juce::TextEditor chordEditor;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(ChordInputComponent)
};
