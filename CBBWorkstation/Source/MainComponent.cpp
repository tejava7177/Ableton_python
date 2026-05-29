#include "MainComponent.h"

MainComponent::MainComponent()
{
    titleLabel.setText("C.B.B Workstation", juce::dontSendNotification);
    titleLabel.setFont(juce::FontOptions(28.0f, juce::Font::bold));
    titleLabel.setJustificationType(juce::Justification::centredLeft);
    addAndMakeVisible(titleLabel);

    subtitleLabel.setText("Practice-friendly accompaniment workstation prototype", juce::dontSendNotification);
    subtitleLabel.setJustificationType(juce::Justification::centredLeft);
    addAndMakeVisible(subtitleLabel);

    styleLabel.setText("Backing Style", juce::dontSendNotification);
    styleLabel.setJustificationType(juce::Justification::centredLeft);
    addAndMakeVisible(styleLabel);

    styleSelector.addItem("Pop", static_cast<int>(StyleType::Pop) + 1);
    styleSelector.addItem("J-Pop", static_cast<int>(StyleType::JPop) + 1);
    styleSelector.addItem("Blues", static_cast<int>(StyleType::Blues) + 1);
    styleSelector.addItem("Ballad", static_cast<int>(StyleType::Ballad) + 1);
    styleSelector.setSelectedId(static_cast<int>(StyleType::Pop) + 1);
    addAndMakeVisible(styleSelector);

    addAndMakeVisible(chordInputComponent);
    addAndMakeVisible(sectionPanelComponent);
    addAndMakeVisible(grooveControlComponent);
    addAndMakeVisible(transportComponent);

    setSize(1120, 840);
}

void MainComponent::paint(juce::Graphics& g)
{
    g.fillAll(juce::Colour::fromRGB(20, 24, 30));

    auto area = getLocalBounds().reduced(24);
    g.setColour(juce::Colour::fromRGB(34, 40, 50));
    g.fillRoundedRectangle(area.toFloat(), 18.0f);

    g.setColour(juce::Colour::fromRGB(54, 62, 76));
    g.drawRoundedRectangle(area.toFloat(), 18.0f, 2.0f);
}

void MainComponent::resized()
{
    auto area = getLocalBounds().reduced(32);

    auto header = area.removeFromTop(76);
    titleLabel.setBounds(header.removeFromTop(34));
    subtitleLabel.setBounds(header.removeFromTop(22));

    auto styleArea = area.removeFromTop(60);
    styleLabel.setBounds(styleArea.removeFromLeft(160));
    styleSelector.setBounds(styleArea.removeFromLeft(240).reduced(0, 8));

    area.removeFromTop(12);
    chordInputComponent.setBounds(area.removeFromTop(104));

    area.removeFromTop(12);
    auto middleRow = area.removeFromTop(240);
    sectionPanelComponent.setBounds(middleRow.removeFromLeft(middleRow.proportionOfWidth(0.48f)));
    middleRow.removeFromLeft(16);
    grooveControlComponent.setBounds(middleRow);

    area.removeFromTop(12);
    transportComponent.setBounds(area.removeFromTop(130));
}
