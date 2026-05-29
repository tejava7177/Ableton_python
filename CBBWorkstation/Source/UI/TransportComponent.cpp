#include "TransportComponent.h"

TransportComponent::TransportComponent()
{
    titleLabel.setText("Transport", juce::dontSendNotification);
    titleLabel.setJustificationType(juce::Justification::centredLeft);
    addAndMakeVisible(titleLabel);

    statusLabel.setText("Ready", juce::dontSendNotification);
    statusLabel.setJustificationType(juce::Justification::centredLeft);
    addAndMakeVisible(statusLabel);

    addAndMakeVisible(playButton);
    addAndMakeVisible(stopButton);
}

void TransportComponent::paint(juce::Graphics& g)
{
    g.setColour(juce::Colour::fromRGB(42, 48, 60));
    g.fillRoundedRectangle(getLocalBounds().toFloat(), 14.0f);
}

void TransportComponent::resized()
{
    auto area = getLocalBounds().reduced(20);
    titleLabel.setBounds(area.removeFromTop(24));
    area.removeFromTop(16);

    auto controlRow = area.removeFromTop(40);
    playButton.setBounds(controlRow.removeFromLeft(140));
    controlRow.removeFromLeft(12);
    stopButton.setBounds(controlRow.removeFromLeft(140));

    area.removeFromTop(14);
    statusLabel.setBounds(area.removeFromTop(28));
}

