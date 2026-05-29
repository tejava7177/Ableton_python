#include "ChordInputComponent.h"

ChordInputComponent::ChordInputComponent()
{
    titleLabel.setText("Chord Progression", juce::dontSendNotification);
    titleLabel.setJustificationType(juce::Justification::centredLeft);
    addAndMakeVisible(titleLabel);

    chordEditor.setText("C - G - Am - F", juce::dontSendNotification);
    chordEditor.setFont(juce::FontOptions(20.0f));
    chordEditor.setMultiLine(false);
    addAndMakeVisible(chordEditor);
}

void ChordInputComponent::paint(juce::Graphics& g)
{
    g.setColour(juce::Colour::fromRGB(42, 48, 60));
    g.fillRoundedRectangle(getLocalBounds().toFloat(), 14.0f);
}

void ChordInputComponent::resized()
{
    auto area = getLocalBounds().reduced(20);
    titleLabel.setBounds(area.removeFromTop(24));
    area.removeFromTop(12);
    chordEditor.setBounds(area.removeFromTop(44));
}

juce::String ChordInputComponent::getChordText() const
{
    return chordEditor.getText();
}

