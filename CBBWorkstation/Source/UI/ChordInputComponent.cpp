#include "ChordInputComponent.h"

ChordInputComponent::ChordInputComponent()
{
    titleLabel.setText("Chord Progression", juce::dontSendNotification);
    titleLabel.setJustificationType(juce::Justification::centredLeft);
    titleLabel.setFont(juce::FontOptions(24.0f, juce::Font::bold));
    addAndMakeVisible(titleLabel);

    helperLabel.setText("Type a progression with '-' separators. Example: C - G - Am - F", juce::dontSendNotification);
    helperLabel.setJustificationType(juce::Justification::centredLeft);
    helperLabel.setColour(juce::Label::textColourId, juce::Colour::fromRGB(165, 178, 194));
    addAndMakeVisible(helperLabel);

    chordEditor.setText("C - G - Am - F", juce::dontSendNotification);
    chordEditor.setFont(juce::FontOptions(26.0f, juce::Font::bold));
    chordEditor.setMultiLine(false);
    chordEditor.setJustification(juce::Justification::centredLeft);
    chordEditor.onTextChange = [this]
    {
        if (onChordChange != nullptr)
            onChordChange();
    };
    addAndMakeVisible(chordEditor);
}

void ChordInputComponent::paint(juce::Graphics& g)
{
    g.setColour(juce::Colour::fromRGB(44, 51, 64));
    g.fillRoundedRectangle(getLocalBounds().toFloat(), 18.0f);
}

void ChordInputComponent::resized()
{
    auto area = getLocalBounds().reduced(28);
    titleLabel.setBounds(area.removeFromTop(30));
    helperLabel.setBounds(area.removeFromTop(24));
    area.removeFromTop(18);
    chordEditor.setBounds(area.removeFromTop(58));
}

juce::String ChordInputComponent::getChordText() const
{
    return chordEditor.getText();
}

void ChordInputComponent::setOnChordChange(std::function<void()> callback)
{
    onChordChange = std::move(callback);
}
