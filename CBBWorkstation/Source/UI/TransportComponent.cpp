#include "TransportComponent.h"

TransportComponent::TransportComponent()
{
    titleLabel.setText("Transport", juce::dontSendNotification);
    titleLabel.setJustificationType(juce::Justification::centredLeft);
    addAndMakeVisible(titleLabel);

    statusLabel.setJustificationType(juce::Justification::centred);
    statusLabel.setColour(juce::Label::backgroundColourId, juce::Colour::fromRGB(24, 30, 36));
    statusLabel.setColour(juce::Label::outlineColourId, juce::Colour::fromRGB(120, 132, 144));
    statusLabel.setColour(juce::Label::textColourId, juce::Colours::white);
    setStatusText("Ready");
    addAndMakeVisible(statusLabel);

    addAndMakeVisible(playButton);
    addAndMakeVisible(stopButton);

    playButton.onClick = [this] { setStatusText("Playing"); };
    stopButton.onClick = [this] { setStatusText("Stopped"); };
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
    area.removeFromTop(14);

    auto controlRow = area.removeFromTop(44);
    playButton.setBounds(controlRow.removeFromLeft(140));
    controlRow.removeFromLeft(12);
    stopButton.setBounds(controlRow.removeFromLeft(140));
    controlRow.removeFromLeft(18);
    statusLabel.setBounds(controlRow.removeFromLeft(140));
}

juce::String TransportComponent::getStatusText() const
{
    return statusLabel.getText();
}

void TransportComponent::setStatusText(const juce::String& newStatus)
{
    statusLabel.setText(newStatus, juce::dontSendNotification);
}
