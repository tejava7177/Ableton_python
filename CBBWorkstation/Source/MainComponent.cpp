#include "MainComponent.h"

#include "Engine/ChordParser.h"

MainComponent::MainComponent()
{
    titleLabel.setText("ChordFlow Workstation", juce::dontSendNotification);
    titleLabel.setFont(juce::FontOptions(28.0f, juce::Font::bold));
    titleLabel.setJustificationType(juce::Justification::centredLeft);
    addAndMakeVisible(titleLabel);

    subtitleLabel.setText("Turn chord progressions into practice-ready backing tracks", juce::dontSendNotification);
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
    styleSelector.onChange = [this] { refreshGeneratedPreview(); };
    addAndMakeVisible(styleSelector);

    optionsHintLabel.setText("Choose a style, shape the groove, then generate a backing track.", juce::dontSendNotification);
    optionsHintLabel.setJustificationType(juce::Justification::centredLeft);
    optionsHintLabel.setColour(juce::Label::textColourId, juce::Colour::fromRGB(165, 178, 194));
    addAndMakeVisible(optionsHintLabel);

    addAndMakeVisible(chordInputComponent);
    addAndMakeVisible(sectionPanelComponent);
    addAndMakeVisible(grooveControlComponent);
    addAndMakeVisible(backingSummaryComponent);
    addAndMakeVisible(transportComponent);

    chordInputComponent.setOnChordChange([this] { refreshGeneratedPreview(); });
    sectionPanelComponent.setOnSectionChange([this](SectionType) { refreshGeneratedPreview(); });
    grooveControlComponent.setOnGrooveChange([this] { refreshGeneratedPreview(); });
    transportComponent.setOnGenerate([this] { generateBacking(false); });
    transportComponent.setOnPlay([this] { generateBacking(true); });
    transportComponent.setOnStop([this]
    {
        playbackEngine.stop();
        transportComponent.setStatusText("Playback stopped. Adjust the setup or generate again.");
    });

    setSize(1120, 840);
    refreshGeneratedPreview();
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

    chordInputComponent.setBounds(area.removeFromTop(156));
    area.removeFromTop(18);

    auto styleArea = area.removeFromTop(58);
    styleLabel.setBounds(styleArea.removeFromLeft(160));
    styleSelector.setBounds(styleArea.removeFromLeft(240).reduced(0, 8));
    styleArea.removeFromLeft(20);
    optionsHintLabel.setBounds(styleArea);

    area.removeFromTop(16);
    auto middleRow = area.removeFromTop(154);
    sectionPanelComponent.setBounds(middleRow.removeFromLeft(middleRow.proportionOfWidth(0.48f)));
    middleRow.removeFromLeft(16);
    grooveControlComponent.setBounds(middleRow);

    area.removeFromTop(18);
    backingSummaryComponent.setBounds(area.removeFromTop(216));

    area.removeFromTop(18);
    transportComponent.setBounds(area.removeFromTop(156));
}

void MainComponent::refreshGeneratedPreview()
{
    const auto parsedProgression = Engine::ChordParser::parse(chordInputComponent.getChordText());

    if (! parsedProgression.isValid)
    {
        backingSummaryComponent.setSummary("Invalid progression",
                                           "Drums: waiting for valid chords",
                                           "Bass: waiting for valid chords",
                                           "Feel: adjust after chord input",
                                           parsedProgression.message);
        if (! playbackEngine.isPlaying())
            transportComponent.setStatusText("Enter a valid chord progression to continue.");
        return;
    }

    const auto generatedPattern = patternGenerator.prepare(parsedProgression.chords,
                                                           getSelectedStyle(),
                                                           sectionPanelComponent.getSelectedSection(),
                                                           grooveControlComponent.getEnergy(),
                                                           grooveControlComponent.getSwing());

    backingSummaryComponent.setSummary(getSelectedStyle() == StyleType::JPop ? "J-Pop / " + getSectionText()
                                                                             : styleSelector.getText() + " / " + getSectionText(),
                                       "Drums: " + generatedPattern.drumPattern,
                                       "Bass: " + generatedPattern.bassPattern,
                                       "Feel: " + getEnergyText() + " energy, " + getSwingText() + " swing",
                                       "Ready to generate a " + styleSelector.getText() + " backing for "
                                           + juce::String(parsedProgression.chords.size()) + " chords.");

    if (! playbackEngine.isPlaying())
        transportComponent.setStatusText("Setup ready. Generate to lock in the backing, or press Play to start immediately.");
}

void MainComponent::generateBacking(bool shouldStartPlayback)
{
    const auto parsedProgression = Engine::ChordParser::parse(chordInputComponent.getChordText());
    if (! parsedProgression.isValid)
    {
        transportComponent.setStatusText(parsedProgression.message);
        return;
    }

    const auto generatedPattern = patternGenerator.prepare(parsedProgression.chords,
                                                           getSelectedStyle(),
                                                           sectionPanelComponent.getSelectedSection(),
                                                           grooveControlComponent.getEnergy(),
                                                           grooveControlComponent.getSwing());

    backingSummaryComponent.setSummary(styleSelector.getText() + " / " + getSectionText(),
                                       "Drums: " + generatedPattern.drumPattern,
                                       "Bass: " + generatedPattern.bassPattern,
                                       "Feel: " + getEnergyText() + " energy, " + getSwingText() + " swing",
                                       "Generated backing ready for practice over "
                                           + juce::String(parsedProgression.chords.size()) + " chords.");

    if (! shouldStartPlayback)
    {
        playbackEngine.stop();
        transportComponent.setStatusText("Backing generated. Review the groove summary, then press Play.");
        return;
    }

    playbackEngine.play(generatedPattern.description, transportComponent.isLoopEnabled());
    auto statusText = "Playing " + styleSelector.getText() + " backing in " + getSectionText();
    if (playbackEngine.isLoopEnabled())
        statusText += " with loop enabled.";
    else
        statusText += ".";
    transportComponent.setStatusText(statusText);
}

StyleType MainComponent::getSelectedStyle() const noexcept
{
    const auto selected = styleSelector.getSelectedId() - 1;
    if (selected < 0)
        return StyleType::Pop;

    return static_cast<StyleType>(selected);
}

juce::String MainComponent::getSectionText() const
{
    switch (sectionPanelComponent.getSelectedSection())
    {
        case SectionType::MainA: return "Main A";
        case SectionType::Fill: return "Fill";
        case SectionType::Ending: return "Ending";
    }

    return "Main A";
}

juce::String MainComponent::getEnergyText() const
{
    const auto energy = grooveControlComponent.getEnergy();
    if (energy < 0.34f)
        return "Low";
    if (energy < 0.67f)
        return "Medium";
    return "High";
}

juce::String MainComponent::getSwingText() const
{
    const auto swing = grooveControlComponent.getSwing();
    if (swing < 0.2f)
        return "Straight";
    if (swing < 0.6f)
        return "Light";
    return "Heavy";
}
