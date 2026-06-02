#include "BackingSummaryComponent.h"

BackingSummaryComponent::BackingSummaryComponent()
{
    titleLabel.setText("Generated Backing", juce::dontSendNotification);
    titleLabel.setJustificationType(juce::Justification::centredLeft);
    titleLabel.setFont(juce::FontOptions(24.0f, juce::Font::bold));
    addAndMakeVisible(titleLabel);

    subtitleLabel.setText("Review the rhythm section before you start practicing.", juce::dontSendNotification);
    subtitleLabel.setJustificationType(juce::Justification::centredLeft);
    subtitleLabel.setColour(juce::Label::textColourId, juce::Colour::fromRGB(165, 178, 194));
    addAndMakeVisible(subtitleLabel);

    configureInfoLabel(styleSectionLabel);
    configureInfoLabel(drumsLabel);
    configureInfoLabel(bassLabel);
    configureInfoLabel(feelLabel);

    helperLabel.setJustificationType(juce::Justification::centredLeft);
    helperLabel.setColour(juce::Label::textColourId, juce::Colour::fromRGB(210, 218, 228));
    addAndMakeVisible(helperLabel);
}

void BackingSummaryComponent::paint(juce::Graphics& g)
{
    g.setColour(juce::Colour::fromRGB(44, 51, 64));
    g.fillRoundedRectangle(getLocalBounds().toFloat(), 18.0f);

    auto area = getLocalBounds().reduced(20);
    area.removeFromTop(86);

    const auto cardWidth = (area.getWidth() - 24) / 3;
    const auto cardHeight = 82;
    drawInfoCard(g, area.removeFromLeft(cardWidth).removeFromTop(cardHeight));
    area.removeFromLeft(12);
    drawInfoCard(g, area.removeFromLeft(cardWidth).removeFromTop(cardHeight));
    area.removeFromLeft(12);
    drawInfoCard(g, area.removeFromLeft(cardWidth).removeFromTop(cardHeight));

    area = getLocalBounds().reduced(20);
    area.removeFromTop(180);
    drawInfoCard(g, area.removeFromTop(56));
}

void BackingSummaryComponent::resized()
{
    auto area = getLocalBounds().reduced(20);

    titleLabel.setBounds(area.removeFromTop(30));
    subtitleLabel.setBounds(area.removeFromTop(26));
    area.removeFromTop(16);

    auto infoRow = area.removeFromTop(82);
    const auto cardWidth = (infoRow.getWidth() - 24) / 3;

    auto firstBounds = infoRow.removeFromLeft(cardWidth).reduced(16, 12);
    styleSectionLabel.setBounds(firstBounds.removeFromTop(28));
    drumsLabel.setBounds(firstBounds);

    auto remainingInfoRow = infoRow;
    remainingInfoRow.removeFromLeft(12);
    auto secondBounds = remainingInfoRow.removeFromLeft(cardWidth).reduced(16, 12);
    bassLabel.setBounds(secondBounds);

    remainingInfoRow.removeFromLeft(12);
    auto thirdBounds = remainingInfoRow.removeFromLeft(cardWidth).reduced(16, 12);
    feelLabel.setBounds(thirdBounds);

    area.removeFromTop(16);
    helperLabel.setBounds(area.removeFromTop(56).reduced(16, 10));
}

void BackingSummaryComponent::setSummary(const juce::String& styleSectionText,
                                         const juce::String& drumsText,
                                         const juce::String& bassText,
                                         const juce::String& feelText,
                                         const juce::String& helperText)
{
    styleSectionLabel.setText(styleSectionText, juce::dontSendNotification);
    drumsLabel.setText(drumsText, juce::dontSendNotification);
    bassLabel.setText(bassText, juce::dontSendNotification);
    feelLabel.setText(feelText, juce::dontSendNotification);
    helperLabel.setText(helperText, juce::dontSendNotification);
}

void BackingSummaryComponent::configureInfoLabel(juce::Label& label)
{
    label.setJustificationType(juce::Justification::centredLeft);
    label.setColour(juce::Label::textColourId, juce::Colours::white);
    label.setFont(juce::FontOptions(18.0f, juce::Font::bold));
    addAndMakeVisible(label);
}

void BackingSummaryComponent::drawInfoCard(juce::Graphics& g, juce::Rectangle<int> bounds) const
{
    g.setColour(juce::Colour::fromRGB(31, 37, 46));
    g.fillRoundedRectangle(bounds.toFloat().reduced(0.0f, 2.0f), 14.0f);

    g.setColour(juce::Colour::fromRGB(76, 87, 104));
    g.drawRoundedRectangle(bounds.toFloat().reduced(0.5f, 2.5f), 14.0f, 1.0f);
}
