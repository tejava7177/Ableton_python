#pragma once

#include <functional>

#include <juce_gui_extra/juce_gui_extra.h>

class ChordInputComponent final : public juce::Component
{
public:
    ChordInputComponent();

    void paint(juce::Graphics& g) override;
    void resized() override;

    [[nodiscard]] juce::String getChordText() const;
    void setOnChordChange(std::function<void()> callback);

private:
    juce::Label titleLabel;
    juce::TextEditor chordEditor;
    std::function<void()> onChordChange;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(ChordInputComponent)
};
