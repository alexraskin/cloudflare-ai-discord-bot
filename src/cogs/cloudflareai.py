from __future__ import annotations

import os
import time

from io import BytesIO
from typing import Optional

import discord
from discord import app_commands
from discord.app_commands import command
from discord.ext.commands import GroupCog

from cloudflareai import (
    CloudflareAI,
    AiTextToImageModels,
    AiTextGenerationModels,
    AiImageClassificationModels,
    AiSpeechRecognitionModels,
    AiTranslationModels,
    TranslationLanguages,
)


class Ai(GroupCog, name="cloudflareai"):
    def __init__(self, client: discord.commands.Bot) -> None:
        self.client: discord.commands.Bot = client
        self.ai = CloudflareAI(
            Cloudflare_API_Key=os.getenv("CLOUDFLARE_API_KEY"),
            Cloudflare_Account_Identifier=os.getenv("CLOUDFLARE_ACCOUNT_IDENTIFIER"),
        )

    @command(name="image_generation")
    @app_commands.describe(text="The text to generate an image from.")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def text_to_image(
        self,
        interaction: discord.Interaction,
        text: str,
    ) -> None:
        """Generate an image from a given text."""
        await interaction.response.defer()
        start_time = time.time()
        try:
            image = await self.ai.TextToImage(
                prompt=text,
                model_name=AiTextToImageModels.XL_BASE,
            )
            if image.status_code != 200:
                self.client.log.error(
                    f"The Cloudflare AI returned an error: {image.status_code} {image.reason}"
                )
                await interaction.edit_original_response(
                    f"The Cloudflare AI returned an error: {image.status_code} {image.reason}"
                )
                return
            with BytesIO(image.image) as buffer:
                image_file: discord.File = discord.File(
                    fp=buffer, filename=f"image.png"
                )
                embed = discord.Embed()
                embed.colour = discord.Colour.blurple()
                embed.title = "AI Image Generation Result"
                embed.description = f"```{text}```"
                embed.set_image(url=f"attachment://image.png")
                elapsed_time = time.time() - start_time
                embed.timestamp = interaction.created_at
                embed.set_footer(
                    text=f"Cloudflare AI | Elapsed time: {elapsed_time:.2f} seconds"
                )
                await interaction.edit_original_response(
                    embed=embed, attachments=[image_file]
                )
        except Exception as e:
            self.client.log.error(f"An error occurred: {e}")
            await interaction.edit_original_response(
                f"An error occurred, please try again later"
            )

    @text_to_image.error
    async def text_to_image_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send(
                f"This command is on cooldown, please try again in {error.retry_after:.2f} seconds."
            )
            self.client.log.error(f"An error occurred: {error}")

    @command(name="text_generation")
    @app_commands.describe(user_prompt="The user prompt to use for text generation")
    @app_commands.describe(model="The model to use for text generation.")
    @app_commands.describe(system_prompt="The system prompt to use.")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def text_generation(
        self,
        interaction: discord.Interaction,
        user_prompt: str,
        model: AiTextGenerationModels,
        system_prompt: Optional[str] = "You are an AI assistant, you are very helpful.",
    ) -> None:
        """Generate text from a given prompt."""
        await interaction.response.defer()
        try:
          data = await self.ai.TextGeneration(
              prompt=user_prompt, system_prompt=system_prompt, model_name=model
          )
          self.client.log.info(data.text)
          if data.status_code != 200:
              await interaction.edit_original_response(
                  f"The Cloudflare AI returned an error: {data.status_code} {data.reason}"
              )
              return
        except Exception as e:
            self.client.log.error(f"An error occurred: {e}")
            await interaction.edit_original_response(
                f"An error occurred, please try again later"
            )
            return
        await interaction.edit_original_response(content=data.text)

    @text_generation.error
    async def text_generation_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send(
                f"This command is on cooldown, please try again in {error.retry_after:.2f} seconds."
            )

    @command(name="image_classification")
    @app_commands.describe(image="The image to classify.")
    async def image_classification(
        self,
        interaction: discord.Interaction,
        image: discord.Attachment,
    ) -> None:
        """Classify an image."""
        try:
            image_data = await image.read()
            data = await self.ai.ImageClassification(image_data, model_name=AiImageClassificationModels.RESNET_50)
            await interaction.response.send_message(data)
            if data.status_code != 200:
                await interaction.response.send_message(
                    f"The Cloudflare AI returned an error: {data.status_code} {data.reason}"
                )
                return
        except Exception as e:
            self.client.log.error(f"An error occurred: {e}")
            await interaction.response.send_message(
                f"An error occurred, please try again later"
            )

    @command(name="speech_recognition")
    @app_commands.describe(audio_file="The audio file to recognize speech from.")
    async def speech_recognition(
        self,
        interaction: discord.Interaction,
        audio_file: discord.Attachment,
    ) -> None:
        """Recognize speech from an audio file."""
        try:
            audio = await audio.read()
            data = await self.ai.SpeechRecognition(audio_file, model_name=AiSpeechRecognitionModels.WHISPER)
            await interaction.response.send_message(data)
            if data.status_code != 200:
                await interaction.response.send_message(
                    f"The Cloudflare AI returned an error: {data.status_code} {data.reason}"
                )
                return
        except Exception as e:
            self.client.log.error(f"An error occurred: {e}")
            await interaction.response.send_message(
                f"An error occurred, please try again later"
            )

    @command(name="translation")
    @app_commands.describe(text="The text to translate.")
    @app_commands.describe(source_language="The source language.")
    @app_commands.describe(target_language="The target language.")
    async def translation(
        self,
        interaction: discord.Interaction,
        text: str,
        source_language: TranslationLanguages,
        target_language: TranslationLanguages,
    ) -> None:
        """Translate a given text."""
        await interaction.response.defer()
        try:
            data = await self.ai.Translation(
                text=text,
                source_lang=source_language,
                target_lang=target_language,
                model_name=AiTranslationModels.META_100
            )
            if data.status_code != 200:
                await interaction.edit_original_response(
                    content=f"The Cloudflare AI returned an error: {data.status_code} {data.reason}"
                )
                return
            await interaction.edit_original_response(content=data.text)
        except Exception as e:
            self.client.log.error(f"An error occurred: {e}")
            await interaction.edit_original_response(
                f"An error occurred, please try again later"
            )
            return

async def setup(client: discord.commands.Bot) -> None:
    await client.add_cog(Ai(client))
