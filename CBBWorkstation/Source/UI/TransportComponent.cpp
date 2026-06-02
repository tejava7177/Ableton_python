#include "TransportComponent.h"

TransportComponent::TransportComponent()
{
    titleLabel.setText("Practice Controls", juce::dontSendNotification);
    titleLabel.setJustificationType(juce::Justification::centredLeft);
    titleLabel.setFont(juce::FontOptions(20.0f, juce::Font::bold));
    addAndMakeVisible(titleLabel);

    statusLabel.setJustificationType(juce::Justification::centredLeft);
    statusLabel.setColour(juce::Label::backgroundColourId, juce::Colour::fromRGB(31, 37, 46));
    statusLabel.setColour(juce::Label::outlineColourId, juce::Colour::fromRGB(92, 104, 120));
    statusLabel.setColour(juce::Label::textColourId, juce::Colours::white);
    setStatusText("Generate a backing track to review the current setup.");
    addAndMakeVisible(statusLabel);

    addAndMakeVisible(generateButton);
    addAndMakeVisible(playButton);
    addAndMakeVisible(stopButton);
    addAndMakeVisible(loopButton);

    generateButton.onClick = [this]
    {
        if (onGenerate != nullptr)
            onGenerate();
    };

    playButton.onClick = [this]
    {
        if (onPlay != nullptr)
            onPlay();
    };

    stopButton.onClick = [this]
    {
        if (onStop != nullptr)
            onStop();
    };
}

void TransportComponent::paint(juce::Graphics& g)
{
    g.setColour(juce::Colour::fromRGB(44, 51, 64));
    g.fillRoundedRectangle(getLocalBounds().toFloat(), 18.0f);
}

void TransportComponent::resized()
{
    auto area = getLocalBounds().reduced(24);
    titleLabel.setBounds(area.removeFromTop(28));
    area.removeFromTop(16);

    auto controlRow = area.removeFromTop(44);
    generateButton.setBounds(controlRow.removeFromLeft(220));
    controlRow.removeFromLeft(12);
    playButton.setBounds(controlRow.removeFromLeft(140));
    controlRow.removeFromLeft(12);
    stopButton.setBounds(controlRow.removeFromLeft(140));
    controlRow.removeFromLeft(12);
    loopButton.setBounds(controlRow.removeFromLeft(100));

    area.removeFromTop(16);
    statusLabel.setBounds(area.removeFromTop(54));
}

juce::String TransportComponent::getStatusText() const
{
    return statusLabel.getText();
}

bool TransportComponent::isLoopEnabled() const noexcept
{
    return loopButton.getToggleState();
}

void TransportComponent::setOnGenerate(std::function<void()> callback)
{
    onGenerate = std::move(callback);
}

void TransportComponent::setOnPlay(std::function<void()> callback)
{
    onPlay = std::move(callback);
}

void TransportComponent::setOnStop(std::function<void()> callback)
{
    onStop = std::move(callback);
}

void TransportComponent::setStatusText(const juce::String& newStatus)
{
    statusLabel.setText(newStatus, juce::dontSendNotification);
}
