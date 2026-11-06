"""Multilingual Ad Voiceover & Audio Preview Studio.

Generates high-converting 15s/30s localized voiceover scripts with emotion cues
(Hype, Fail-Ad Rage, Anime/Waifu, Meme Comedy) for 5 global gaming markets (US, JP, KR, BR, VN),
and provides Web Speech API ready parameters for client-side audio preview.
"""

from typing import Dict, Any, List, Optional

class VoiceoverStudio:
    """Generator for localized ad voiceover scripts and speech audio directives."""

    MARKETS = {
        "US": {
            "name": "United States (Tier-1 English)",
            "lang_code": "en-US",
            "locale_notes": "Punchy, dynamic, uses viral TikTok/Twitch streamer slang (No cap, Gigachad, 99% fail, Level 1 Crook vs Level 100 Boss).",
            "default_pitch": 1.05,
            "default_rate": 1.15
        },
        "JP": {
            "name": "Japan (Anime / Seiyuu)",
            "lang_code": "ja-JP",
            "locale_notes": "Dramatic anime voice acting, cute companion waifu or intense battle anime shonen shout (Uso desho?!, Iki yo!, Sugoi).",
            "default_pitch": 1.25,
            "default_rate": 1.10
        },
        "KR": {
            "name": "Korea (Competitive PvP / Flex)",
            "lang_code": "ko-KR",
            "locale_notes": "High APM gamer intensity, bragging about SSR pulls, guild dominance, fast-talking competitive caster cadence (Daebak!, Legend drop, Gacha jackpot).",
            "default_pitch": 1.0,
            "default_rate": 1.20
        },
        "BR": {
            "name": "Brazil (Portuguese Meme / Baile)",
            "lang_code": "pt-BR",
            "locale_notes": "Hyper-expressive, high energy, comedic drama, playful insults, viral Brazilian internet memes (Meu Deus!, Impossível, Bora jogar).",
            "default_pitch": 1.05,
            "default_rate": 1.15
        },
        "VN": {
            "name": "Vietnam (Gen Z Streamer / Drama)",
            "lang_code": "vi-VN",
            "locale_notes": "Streamer reaction style, dramatic fail, viral TikTok phrases, flex VIP 15, hài hước lầy lội (Ảo thật đấy, Cứu tôi với, Game gì mà cuốn thế này).",
            "default_pitch": 1.1,
            "default_rate": 1.15
        }
    }

    EMOTIONS = {
        "hype": {
            "name": "Streamer Hype / Adrenaline Rush",
            "description": "High energy, screaming reaction, intense excitement on legendary drops or clutch victory.",
            "bgm_style": "140 BPM EDM / Trap Beat / Fast Drums",
            "pitch_mod": 1.15,
            "rate_mod": 1.2
        },
        "fail_rage": {
            "name": "Fail-Ad / Rage-Bait ('Why is this so hard?!')",
            "description": "Exaggerated frustration, failing on level 1, challenging user ego to download and prove they can do better.",
            "bgm_style": "Dramatic orchestral suspense + sad violin fail sound",
            "pitch_mod": 0.95,
            "rate_mod": 1.1
        },
        "anime_waifu": {
            "name": "Anime Companion / Sweet & Teasing",
            "description": "Warm, emotional, anime heroine greeting player or pleading for rescue/help in battle.",
            "bgm_style": "Uplifting J-Pop or enchanting fantasy harp & strings",
            "pitch_mod": 1.35,
            "rate_mod": 1.0
        },
        "meme_comedy": {
            "name": "Meme Comedy / Sarcastic Reaction",
            "description": "Deadpan sarcasm, meme sound cues, ironic commentary on mobile gamer stereotypes.",
            "bgm_style": "Quirky 8-bit chip-tune / Goofy cartoon kazoo & slide whistle",
            "pitch_mod": 1.0,
            "rate_mod": 1.15
        }
    }

    def get_supported_markets(self) -> Dict[str, Any]:
        """Returns metadata of supported localization markets."""
        return self.MARKETS

    def get_supported_emotions(self) -> Dict[str, Any]:
        """Returns metadata of supported emotion styles."""
        return self.EMOTIONS

    def generate_voiceover_script(
        self,
        game_title: str = "Shadow Legends War",
        genre: str = "RPG / Strategy",
        target_market: str = "US",
        emotion_tone: str = "hype",
        duration_seconds: int = 15
    ) -> Dict[str, Any]:
        """Generates line-by-line script with audio cues, sfx, screen directions, and TTS payload."""
        market_info = self.MARKETS.get(target_market.upper(), self.MARKETS["US"])
        emotion_info = self.EMOTIONS.get(emotion_tone.lower(), self.EMOTIONS["hype"])
        duration = 30 if duration_seconds >= 25 else 15

        # Script templates tailored per market and emotion
        scripts_library = self._get_script_library(game_title, genre)
        market_key = target_market.upper() if target_market.upper() in scripts_library else "US"
        emotion_key = emotion_tone.lower() if emotion_tone.lower() in scripts_library[market_key] else "hype"
        
        raw_lines = scripts_library[market_key][emotion_key].get(duration, scripts_library[market_key][emotion_key][15])

        full_speech_text = " ".join([line["voice_text"] for line in raw_lines])
        recommended_pitch = round(market_info["default_pitch"] * emotion_info["pitch_mod"] / 1.0, 2)
        recommended_rate = round(market_info["default_rate"] * emotion_info["rate_mod"] / 1.0, 2)

        return {
            "meta": {
                "game_title": game_title,
                "genre": genre,
                "target_market": target_market.upper(),
                "market_name": market_info["name"],
                "lang_code": market_info["lang_code"],
                "emotion_tone": emotion_tone,
                "emotion_name": emotion_info["name"],
                "duration_seconds": duration,
                "bgm_recommendation": emotion_info["bgm_style"],
                "casting_advice": f"Select voice talent with native {market_info['lang_code']} accent and {emotion_info['description'].lower()}"
            },
            "tts_parameters": {
                "lang": market_info["lang_code"],
                "pitch": recommended_pitch,
                "rate": recommended_rate,
                "full_text": full_speech_text
            },
            "timeline": raw_lines,
            "marketing_tactics": {
                "hook_tactic": "Giữ chân trong 3s đầu với âm thanh kích thích hoặc câu hỏi thách thức chỉ số IQ.",
                "mid_roll_tactic": "Đẩy cao trào với SFX dồn dập (jackpot roll, combo hit, explosion) để tăng time-in-ad.",
                "cta_tactic": "Khóa chặt hành vi chuyển đổi bằng từ khóa tải miễn phí kèm quà tặng tân thủ (Free 1000 Pulls / Code VIP)."
            }
        }

    def _get_script_library(self, title: str, genre: str) -> Dict[str, Any]:
        """Localized script variations for 5 markets x 4 emotions x (15s & 30s)."""
        return {
            "US": {
                "hype": {
                    15: [
                        {
                            "time": "00:00 - 00:03",
                            "section": "Hook",
                            "voice_text": f"Wait! Stop scrolling! Did you really think you could beat {title}?",
                            "screen_direction": "Fast zoom into rare 5-star character glowing with lightning effects.",
                            "sfx_cue": "VINYL_SCRATCH + THUNDER_BOOM"
                        },
                        {
                            "time": "00:03 - 00:10",
                            "section": "Action Climax",
                            "voice_text": "Bro just merged 50 Mythic dragons! Look at the damage! Over 9,000,000 DPS! Absolute insanity!",
                            "screen_direction": "Screen shakes violently with critical damage numbers flying everywhere.",
                            "sfx_cue": "RAPID_MACHINE_GUN_HITS + HYPER_CHEERING"
                        },
                        {
                            "time": "00:10 - 00:15",
                            "section": "CTA",
                            "voice_text": f"Download {title} now and claim 777 free summons! Tap the button below!",
                            "screen_direction": "Pulsing golden App Store badge and 'FREE 777 SUMMONS' banner flashing.",
                            "sfx_cue": "COIN_JACKPOT_SHOWER + WHOOSH"
                        }
                    ],
                    30: [
                        {
                            "time": "00:00 - 00:05",
                            "section": "Hook",
                            "voice_text": f"Everyone told me {title} was impossible. So I spent 24 hours grinding straight!",
                            "screen_direction": "Split screen: Player webcam reacting with wild eyes vs Level 1 rookie gameplay.",
                            "sfx_cue": "DRAMATIC_CLOCK_TICK + BASS_DROP"
                        },
                        {
                            "time": "00:05 - 00:15",
                            "section": "Escalation",
                            "voice_text": "Level 1: Wooden stick. Level 50: Fire katana. But wait till you see what happens at Level 100!",
                            "screen_direction": "Rapid montage of weapon morphing into giant celestial blade.",
                            "sfx_cue": "SWORD_CLASH + POWER_UP_ZAP"
                        },
                        {
                            "time": "00:15 - 00:23",
                            "section": "Boss Battle",
                            "voice_text": "One shot on the World Boss! No way! The server leaderboards just broke!",
                            "screen_direction": "World Boss HP bar melts from 100% to 0% in slow-mo with screen glow.",
                            "sfx_cue": "HEAVY_EXPLOSION + LEVEL_UP_FANFARE"
                        },
                        {
                            "time": "00:23 - 00:30",
                            "section": "CTA",
                            "voice_text": f"Join my guild right now. Search {title} on Google Play and App Store. Download free!",
                            "screen_direction": "Endcard showing gift code 'PRO2026' and big Download Now button.",
                            "sfx_cue": "COIN_CASCADE + RETRO_CHIME"
                        }
                    ]
                },
                "fail_rage": {
                    15: [
                        {
                            "time": "00:00 - 00:04",
                            "section": "Hook",
                            "voice_text": "Only people with 140 IQ can pass Stage 3... And clearly I'm not one of them!",
                            "screen_direction": "Finger dragging puzzle piece, hovering nervously over obvious wrong slot.",
                            "sfx_cue": "COMIC_HONK + TICK_TOCK"
                        },
                        {
                            "time": "00:04 - 00:10",
                            "section": "Rage Fail",
                            "voice_text": "No! Don't touch the red gate! Ahh! Why does this always happen to me?!",
                            "screen_direction": "Huge red 'FAILED!' stamp slams onto screen as character tumbles into water.",
                            "sfx_cue": "LOUD_BUZZER + CARTOON_SLIP_FALL"
                        },
                        {
                            "time": "00:10 - 00:15",
                            "section": "CTA",
                            "voice_text": f"Can you do any better? Download {title} now and prove me wrong!",
                            "screen_direction": "Bouncing arrows pointing to the green Install button.",
                            "sfx_cue": "FAIL_TROMBONE + VICTORY_CHIME"
                        }
                    ],
                    30: [
                        {
                            "time": "00:00 - 00:06",
                            "section": "Hook",
                            "voice_text": "My mom told me this game was easy. Mom vs Me, let's see who is the real master!",
                            "screen_direction": "Side by side comparison: Mom (Level 99 Pro) vs Me (Level 1 Noob).",
                            "sfx_cue": "WHISTLE_POP + CHEER"
                        },
                        {
                            "time": "00:06 - 00:16",
                            "section": "The Struggle",
                            "voice_text": "She easily dodges every trap while I get flattened by a giant boulder in 3 seconds!",
                            "screen_direction": "Slow-mo replay of character getting crushed comically with flat squish effect.",
                            "sfx_cue": "SQUISH_SOUND + SQUEAKY_TOY"
                        },
                        {
                            "time": "00:16 - 00:24",
                            "section": "Revenge",
                            "voice_text": "Wait! If I use this secret combination... Yes! Wait, no! Not again!",
                            "screen_direction": "Player almost reaches the exit door before falling into pit at last pixel.",
                            "sfx_cue": "DRAMATIC_HEARTBEAT + RAGE_SLAP"
                        },
                        {
                            "time": "00:24 - 00:30",
                            "section": "CTA",
                            "voice_text": f"I bet 99% of you can't beat Mom's high score. Install {title} and test your brain!",
                            "screen_direction": "Endcard with high score leaderboard and direct app link.",
                            "sfx_cue": "SWOOSH + GAME_OVER_CHIME"
                        }
                    ]
                },
                "anime_waifu": {
                    15: [
                        {
                            "time": "00:00 - 00:04",
                            "section": "Hook",
                            "voice_text": f"Commander! You finally answered my summon in {title}!",
                            "screen_direction": "Anime heroine reaches hand toward camera with sparkling eyes and cherry blossoms.",
                            "sfx_cue": "MAGICAL_SPARKLE + CHIME"
                        },
                        {
                            "time": "00:04 - 00:10",
                            "section": "Battle Call",
                            "voice_text": "The dark legions are invading our sanctuary! Command my blade and unleash our ultimate!",
                            "screen_direction": "Cinematic cut-in of anime ultimate burst animation with glowing aura.",
                            "sfx_cue": "SWORD_UNSHEATHE + ENERGY_BEAM"
                        },
                        {
                            "time": "00:10 - 00:15",
                            "section": "CTA",
                            "voice_text": "I will protect you with my life! Tap install to stand by my side today!",
                            "screen_direction": "Heroine smiles gently while card collection carousel spins.",
                            "sfx_cue": "HARP_GLISSANDO + HEART_POP"
                        }
                    ],
                    30: [
                        {
                            "time": "00:00 - 00:08",
                            "section": "Hook",
                            "voice_text": f"Senpai, where have you been? The kingdom has been waiting for its true ruler in {title}!",
                            "screen_direction": "Close-up emotional 2D live anime model with teary, determined expression.",
                            "sfx_cue": "PIANO_MELODY + WIND_CHIMES"
                        },
                        {
                            "time": "00:08 - 00:18",
                            "section": "Gameplay Showcase",
                            "voice_text": "Choose from over 80 unique heroes, customize their abilities, and forge our destiny together!",
                            "screen_direction": "Showcase of character roster with rich animations and voice line snippets.",
                            "sfx_cue": "PAGE_SWIPE + WEAPON_EQUIP"
                        },
                        {
                            "time": "00:18 - 00:24",
                            "section": "Ultimate Attack",
                            "voice_text": "Together, our bond is unbreakable! Celestial Burst, activate!",
                            "screen_direction": "Screen-filling neon anime ultimate spell destroying entire wave of enemy minions.",
                            "sfx_cue": "LASER_BLAST + CRYSTAL_SHATTER"
                        },
                        {
                            "time": "00:24 - 00:30",
                            "section": "CTA",
                            "voice_text": "Get an exclusive SSR Hero for free on your first day! Download now, Senpai!",
                            "screen_direction": "Endcard featuring SSR card showcase and glowing Free Download button.",
                            "sfx_cue": "SPARKLE_FANFARE"
                        }
                    ]
                },
                "meme_comedy": {
                    15: [
                        {
                            "time": "00:00 - 00:04",
                            "section": "Hook",
                            "voice_text": "Mobile ads say: You will win a Tesla! What actually happens in the game:",
                            "screen_direction": "Exaggerated fake car image turns into tiny rubber duck on a skateboard.",
                            "sfx_cue": "RECORD_SCRATCH + QUACK"
                        },
                        {
                            "time": "00:04 - 00:10",
                            "section": "Meme Reality",
                            "voice_text": "Wait, why is this duck actually kicking so much butt?! He just roasted an entire dragon army!",
                            "screen_direction": "Rubber duck shoots laser eyes in chaotic 8-bit battle madness.",
                            "sfx_cue": "PEW_PEW_LASER + CARTOON_BOING"
                        },
                        {
                            "time": "00:10 - 00:15",
                            "section": "CTA",
                            "voice_text": f"Zero fake ads. Just 100% ridiculous fun. Get {title} right now!",
                            "screen_direction": "Thumb stamping '100% REAL GAMEPLAY' seal with download link.",
                            "sfx_cue": "AIRHORN_BLAST"
                        }
                    ],
                    30: [
                        {
                            "time": "00:00 - 00:08",
                            "section": "Hook",
                            "voice_text": "Therapist: You cannot play mobile games 14 hours a day. Me, 3 minutes into this game:",
                            "screen_direction": "Meme face transition into intense gaming trance under RGB neon lighting.",
                            "sfx_cue": "DRAMATIC_OPERA_NOTE + TYPING_CLATTER"
                        },
                        {
                            "time": "00:08 - 00:18",
                            "section": "Addiction Arc",
                            "voice_text": "I said I'd play one quick round before bed. It's now 4:30 in the morning and my army owns half the map!",
                            "screen_direction": "Time-lapse clock spinning furiously as territory colors expand across world map.",
                            "sfx_cue": "TICKING_FAST_FORWARD + CONQUEST_MARCH"
                        },
                        {
                            "time": "00:18 - 00:24",
                            "section": "The Flex",
                            "voice_text": "My guildmates are sending me pizza so I don't stop defending the castle!",
                            "screen_direction": "Chat bubbles popping up: 'Carry us King!', 'Defend the north wall!'",
                            "sfx_cue": "NOTIFICATION_PING_CHORUS"
                        },
                        {
                            "time": "00:24 - 00:30",
                            "section": "CTA",
                            "voice_text": f"Warning: Extremely addictive. Say goodbye to your sleep schedule. Download {title} free!",
                            "screen_direction": "Endcard with hazard warning tape and flashing Install icon.",
                            "sfx_cue": "SIREN_WOOP_WOOP + CASH_REGISTER"
                        }
                    ]
                }
            },
            "JP": {
                "hype": {
                    15: [
                        {
                            "time": "00:00 - 00:04",
                            "section": "Hook",
                            "voice_text": f"待って！その指を止めて！{title}の最強レジェンドガチャ、引いたことある？",
                            "screen_direction": "Shining rainbow crystal bursting open with dramatic Japanese anime kanji text.",
                            "sfx_cue": "MAGICAL_GONG + RAINBOW_SHINE"
                        },
                        {
                            "time": "00:04 - 00:10",
                            "section": "Action Climax",
                            "voice_text": "SSR確定の金扉キター！この攻撃力…9999万超えだと？！信じられない！",
                            "screen_direction": "Massive fiery critical slash cutting screen in half.",
                            "sfx_cue": "KATANA_SLASH + EXPLOSION"
                        },
                        {
                            "time": "00:10 - 00:15",
                            "section": "CTA",
                            "voice_text": f"今すぐダウンロードで無料1000連ガチャ！{title}で会いましょう！",
                            "screen_direction": "Endcard with '無料1000連' golden banner and shiny app store badge.",
                            "sfx_cue": "FANFARE_TRUMPETS"
                        }
                    ],
                    30: [
                        {
                            "time": "00:00 - 00:08",
                            "section": "Hook",
                            "voice_text": f"全世界待望の超大作RPG、{title}がついに日本上陸！君はこの圧倒的グラフィックに耐えられるか？",
                            "screen_direction": "Panoramic 3D camera pan over massive castle and flying dragon.",
                            "sfx_cue": "CINEMATIC_ORCHESTRAL_SWELL"
                        },
                        {
                            "time": "00:08 - 00:18",
                            "section": "Combat",
                            "voice_text": "全キャラ豪華声優ボイス搭載！タップひとつで繰り出す超必殺奥義！",
                            "screen_direction": "Heroine unleashing frozen crystal ultimate with multi-hit combos.",
                            "sfx_cue": "ICE_SPIKES + SHATTER"
                        },
                        {
                            "time": "00:18 - 00:24",
                            "section": "Raid Boss",
                            "voice_text": "仲間と連携して巨大ボスを討伐せよ！サーバーランキング第1位を掴み取れ！",
                            "screen_direction": "4-player co-op raid boss fight with health bar shattering.",
                            "sfx_cue": "DRUM_ROLL + VICTORY_GONG"
                        },
                        {
                            "time": "00:24 - 00:30",
                            "section": "CTA",
                            "voice_text": f"今登録すると限定SSRキャラを全員にプレゼント！下のボタンをタップ！",
                            "screen_direction": "Endcard with exclusive SSR character card and '今すぐプレイ' button.",
                            "sfx_cue": "SPARKLE_JINGLE"
                        }
                    ]
                },
                "fail_rage": {
                    15: [
                        {
                            "time": "00:00 - 00:04",
                            "section": "Hook",
                            "voice_text": "嘘でしょ？！99%の人がステージ3で詰むってマジ？！",
                            "screen_direction": "Puzzle pin being pulled slowly, lava hovering over hero.",
                            "sfx_cue": "SUSPENSE_STRING + WATER_DROP"
                        },
                        {
                            "time": "00:04 - 00:10",
                            "section": "Rage Fail",
                            "voice_text": "あぁぁ！そこじゃない！溶岩落ちてきたぁぁ！なんで毎回こうなるの？！",
                            "screen_direction": "Lava consumes character, big comic skull appears with 'GAME OVER'.",
                            "sfx_cue": "ANIME_SCREAM + BUZZER"
                        },
                        {
                            "time": "00:10 - 00:15",
                            "section": "CTA",
                            "voice_text": f"あなたならクリアできる？{title}を今すぐダウンロードして挑戦してみて！",
                            "screen_direction": "Pulsing install button with question mark animation.",
                            "sfx_cue": "CARTOON_BOING"
                        }
                    ],
                    30: [
                        {
                            "time": "00:00 - 00:08",
                            "section": "Hook",
                            "voice_text": "ネットで話題の激ムズパズル、絶対にイライラしないって決めてたのに…！",
                            "screen_direction": "Player hands shaking while holding smartphone over level 5 trap.",
                            "sfx_cue": "COMICAL_TIPTOE"
                        },
                        {
                            "time": "00:08 - 00:18",
                            "section": "Frustration",
                            "voice_text": "右に行けばセーフ…と思いきや落とし穴？！ちょっと待って開発者さん意地悪すぎません？！",
                            "screen_direction": "Floor falls out right before the golden chest, character drops.",
                            "sfx_cue": "SLIDE_WHISTLE_DOWN + CRASH"
                        },
                        {
                            "time": "00:18 - 00:24",
                            "section": "Determination",
                            "voice_text": "もう一回！今度こそ…ああっまた引っかかった！悔しすぎる！",
                            "screen_direction": "Instant restart button pressed 5 times frantically.",
                            "sfx_cue": "RAPID_CLICKS + SIGH"
                        },
                        {
                            "time": "00:24 - 00:30",
                            "section": "CTA",
                            "voice_text": f"IQ150以上の天才求む！{title}をインストールして完全クリアを目指せ！",
                            "screen_direction": "Endcard with brain score meter and direct App Store link.",
                            "sfx_cue": "FANFARE_SHORT"
                        }
                    ]
                },
                "anime_waifu": {
                    15: [
                        {
                            "time": "00:00 - 00:04",
                            "section": "Hook",
                            "voice_text": f"ご主人様…やっと戻ってきてくれたのですね！{title}の世界へようこそ！",
                            "screen_direction": "Cute anime maid / fox-girl with animated ears smiling warmly.",
                            "sfx_cue": "HEART_BELL + CHIME"
                        },
                        {
                            "time": "00:04 - 00:10",
                            "section": "Action",
                            "voice_text": "私の力、全部ご主人様に捧げます！一緒に冒険に出かけましょう！",
                            "screen_direction": "Heroine summons sparkling magic circle, dual combat synergy.",
                            "sfx_cue": "MAGIC_WHIRL + CHIME"
                        },
                        {
                            "time": "00:10 - 00:15",
                            "section": "CTA",
                            "voice_text": "私を一人にしないで…今すぐインストールして会いに来てくださいね！",
                            "screen_direction": "Heroine waves goodbye with blushing cheeks, install button pulses pink.",
                            "sfx_cue": "KISS_POP + GENTLE_BELL"
                        }
                    ],
                    30: [
                        {
                            "time": "00:00 - 00:08",
                            "section": "Hook",
                            "voice_text": f"あの…先輩？{title}で先輩のこと、ずっと待ってたんですよ？",
                            "screen_direction": "Soft focus anime school-courtyard / fantasy shrine setting.",
                            "sfx_cue": "GENTLE_ACOUSTIC_GUITAR"
                        },
                        {
                            "time": "00:08 - 00:18",
                            "section": "Bonding",
                            "voice_text": "プレゼントをあげたり、デートしたり…仲良くなると特別なストーリーが解放されちゃうんです！",
                            "screen_direction": "UI showcases intimacy meter filling up, unlocking wedding dress skin.",
                            "sfx_cue": "LOVE_HEART_SPARKLE"
                        },
                        {
                            "time": "00:18 - 00:24",
                            "section": "Climax",
                            "voice_text": "でも戦いでは…先輩を傷つける敵は絶対に許しません！奥義解放！",
                            "screen_direction": "Heroine switches to battle armor with blazing aura and powerful katana strike.",
                            "sfx_cue": "SWORD_DRAW + LASER_BURST"
                        },
                        {
                            "time": "00:24 - 00:30",
                            "section": "CTA",
                            "voice_text": "最初のガチャで最高レア確定！下のボタンから今すぐ私をお迎えしてね！",
                            "screen_direction": "Endcard with high quality waifu portrait and glowing download CTA.",
                            "sfx_cue": "SWEET_CHIME"
                        }
                    ]
                },
                "meme_comedy": {
                    15: [
                        {
                            "time": "00:00 - 00:04",
                            "section": "Hook",
                            "voice_text": "広告あるある：『クリア率0.001%！』…いや難易度設定バグりすぎでしょ！",
                            "screen_direction": "Impossible mathematical formula floating over simple 2D stickman.",
                            "sfx_cue": "DRAMATIC_DUN_DUN_DUN"
                        },
                        {
                            "time": "00:04 - 00:10",
                            "section": "Punchline",
                            "voice_text": "でも実際のゲームは…あれ？普通にめちゃくちゃ面白くて草生えるんだが！",
                            "screen_direction": "Fast-paced satisfying merge action with combo counts x50.",
                            "sfx_cue": "COMICAL_POP + CHEERING"
                        },
                        {
                            "time": "00:10 - 00:15",
                            "section": "CTA",
                            "voice_text": f"無駄な広告なし！本物の面白さを今すぐ体感せよ！{title}！",
                            "screen_direction": "Endcard with green 'DOWNLOAD NOW' badge.",
                            "sfx_cue": "GAME_START_CHIME"
                        }
                    ],
                    30: [
                        {
                            "time": "00:00 - 00:08",
                            "section": "Hook",
                            "voice_text": "『ちょっと5分だけ遊ぼう』そう思っていた時期が僕にもありました。",
                            "screen_direction": "Black and white portrait of tired gamer gazing into phone screen at 3 AM.",
                            "sfx_cue": "SAD_RECORDER_TUNE"
                        },
                        {
                            "time": "00:08 - 00:18",
                            "section": "Meme spiral",
                            "voice_text": "気がついたらギルドマスターに就任して、明日早起きなのに攻城戦の作戦会議してるんだが？！",
                            "screen_direction": "Rapid chat log messages flying by: 'Master, lead the charge!'",
                            "sfx_cue": "FAST_NOTIF_SOUNDS"
                        },
                        {
                            "time": "00:18 - 00:24",
                            "section": "Victory",
                            "voice_text": "でも全サーバー制覇した瞬間の快感…これだからソシャゲはやめられない！",
                            "screen_direction": "Massive gold cup trophy shines with fireworks and confetti.",
                            "sfx_cue": "FIREWORKS_BOOM + APPLAUSE"
                        },
                        {
                            "time": "00:24 - 00:30",
                            "section": "CTA",
                            "voice_text": f"時間泥棒ゲーム警報発令中！睡眠不足に気をつけてダウンロードしてね！{title}！",
                            "screen_direction": "Warning stamp 'TIME THIEF GAME' over download button.",
                            "sfx_cue": "AIRHORN_FUNNY"
                        }
                    ]
                }
            },
            "KR": {
                "hype": {
                    15: [
                        {
                            "time": "00:00 - 00:03",
                            "section": "Hook",
                            "voice_text": f"잠깐만요! 스크롤 멈추세요! {title} 신규 서버 오픈 실화냐?!",
                            "screen_direction": "Electric blue lightning cuts screen revealing new server badge.",
                            "sfx_cue": "ELECTRO_SHOCK + BASS"
                        },
                        {
                            "time": "00:03 - 00:10",
                            "section": "Action Climax",
                            "voice_text": "첫 10연차에 신화급 전설 영웅 떴다! 대박! 전 서버 랭킹 1위 찍으러 갑니다!",
                            "screen_direction": "Golden mythic star explosion with screen shake and critical damage numbers.",
                            "sfx_cue": "JACKPOT_BELLS + CHEERING"
                        },
                        {
                            "time": "00:10 - 00:15",
                            "section": "CTA",
                            "voice_text": f"지금 접속하면 다이아 10만 개 무료 지급! 지금 바로 {title} 다운로드!",
                            "screen_direction": "Gem chest overflowing with 100,000 diamonds, red CTA button pulsing.",
                            "sfx_cue": "COIN_RAIN + TRUMPET"
                        }
                    ],
                    30: [
                        {
                            "time": "00:00 - 00:07",
                            "section": "Hook",
                            "voice_text": f"아직도 양산형 게임 하세요? 진정한 모바일 하드코어 액션의 정점, {title}!",
                            "screen_direction": "Cinematic camera orbiting high-poly armored knight swinging glowing halberd.",
                            "sfx_cue": "HEAVY_SWORD_WOOSH + DRUM_THUMP"
                        },
                        {
                            "time": "00:07 - 00:17",
                            "section": "PvP Combat",
                            "voice_text": "실시간 100인 길드 공성전! 컨트롤 하나로 전세를 뒤집는 짜릿한 손맛!",
                            "screen_direction": "Hundreds of players clashing at castle gates with colorful spells.",
                            "sfx_cue": "WAR_CRY + EXPLOSIONS"
                        },
                        {
                            "time": "00:17 - 00:23",
                            "section": "Achievement",
                            "voice_text": "내가 바로 이 구역의 군주다! 길드원들과 함께 왕좌를 차지하세요!",
                            "screen_direction": "Player character sits on golden throne overlooking conquered fortress.",
                            "sfx_cue": "EPIC_FANFARE"
                        },
                        {
                            "time": "00:23 - 00:30",
                            "section": "CTA",
                            "voice_text": f"구글 플레이, 앱스토어에서 {title} 검색! 사전예약 한정 칭호 지급 중!",
                            "screen_direction": "Endcard featuring app icons and limited edition golden badge.",
                            "sfx_cue": "CLICK_BEEP"
                        }
                    ]
                },
                "fail_rage": {
                    15: [
                        {
                            "time": "00:00 - 00:04",
                            "section": "Hook",
                            "voice_text": "이 게임 광고 보고 비웃었는데… 내가 해보니까 멘붕 오네요!",
                            "screen_direction": "Player character trapped between two closing spikes.",
                            "sfx_cue": "SUSPENSE_RATTLE"
                        },
                        {
                            "time": "00:04 - 00:10",
                            "section": "Fail Moment",
                            "voice_text": "아니 거기서 함정이 나온다고?! 아 진짜 열받네! 한 번만 더 하면 깰 수 있는데!",
                            "screen_direction": "Spikes slam shut, character turns into funny ghost floating away.",
                            "sfx_cue": "BUZZER_FAIL + SAD_VIOLIN"
                        },
                        {
                            "time": "00:10 - 00:15",
                            "section": "CTA",
                            "voice_text": f"당신의 피지컬을 증명해 보세요. 지금 {title} 무료 다운로드!",
                            "screen_direction": "Download button with pulsing heartbeat border.",
                            "sfx_cue": "RETRO_SUCCESS"
                        }
                    ],
                    30: [
                        {
                            "time": "00:00 - 00:08",
                            "section": "Hook",
                            "voice_text": "한국 게이머 특: 절대 못 깬다고 도발하면 밤새워서라도 깸. 저도 도전해 봤습니다!",
                            "screen_direction": "Streamer gaming setup with energy drink and intense focus face.",
                            "sfx_cue": "DRAMATIC_PIANO"
                        },
                        {
                            "time": "00:08 - 00:18",
                            "section": "The Agony",
                            "voice_text": "1단계: 껌이네. 2단계: 어라? 3단계: 야 이거 만든 개발자 누구야 나와봐!",
                            "screen_direction": "Fast cuts of successive hilarious in-game deaths at 99% progress.",
                            "sfx_cue": "PUNCH_SOUND + RAGE_DESK_SLAP"
                        },
                        {
                            "time": "00:18 - 00:24",
                            "section": "The Comeback",
                            "voice_text": "침착하게… 점프, 대시, 회피! 됐다! 깼다아아아! 소리 질러!",
                            "screen_direction": "Ultra clean clutch maneuver dodging five lasers simultaneously.",
                            "sfx_cue": "VICTORY_APPLAUSE + AIRHORN"
                        },
                        {
                            "time": "00:24 - 00:30",
                            "section": "CTA",
                            "voice_text": f"자신 있으면 덤벼보세요. {title} 다운로드하고 랭킹전에서 만납시다!",
                            "screen_direction": "Rank 1 tier badge and App Store download button.",
                            "sfx_cue": "SWOOSH"
                        }
                    ]
                },
                "anime_waifu": {
                    15: [
                        {
                            "time": "00:00 - 00:04",
                            "section": "Hook",
                            "voice_text": f"기사님! 절 구하러 와주신 건가요? {title}에서 기다리고 있었어요!",
                            "screen_direction": "Anime heroine in ruined cathedral extending hand with tearful smile.",
                            "sfx_cue": "CRYSTAL_BELL"
                        },
                        {
                            "time": "00:04 - 00:10",
                            "section": "Action",
                            "voice_text": "기사님과 함께라면 어떤 마왕군도 두렵지 않아요! 빛의 각성 스킬 발동!",
                            "screen_direction": "Giant holy light pillars obliterating dark shadow demons.",
                            "sfx_cue": "HOLY_SPELL_CAST + BEAM"
                        },
                        {
                            "time": "00:10 - 00:15",
                            "section": "CTA",
                            "voice_text": "저와 영원히 함께해 주세요! 지금 설치하고 무료 SSR 영웅을 받으세요!",
                            "screen_direction": "Endcard with heroine smiling and pink install CTA.",
                            "sfx_cue": "GENTLE_FANFARE"
                        }
                    ],
                    30: [
                        {
                            "time": "00:00 - 00:08",
                            "section": "Hook",
                            "voice_text": f"수많은 영웅들과 나누는 가슴 설레는 교감 스토리! {title}에서 당신의 반려 영웅을 찾아보세요.",
                            "screen_direction": "Live2D character interaction showcasing touch reactions and voice clips.",
                            "sfx_cue": "SWEET_BGM_INTRO"
                        },
                        {
                            "time": "00:08 - 00:18",
                            "section": "Features",
                            "voice_text": "호감도를 올릴 때마다 열리는 시크릿 보이스와 화려한 전용 코스튬까지!",
                            "screen_direction": "Costume transformation montage with dazzling particle effects.",
                            "sfx_cue": "CLOTH_SWAP + SPARKLE"
                        },
                        {
                            "time": "00:18 - 00:24",
                            "section": "Combat",
                            "voice_text": "풀 3D 시네마틱 연출로 완성된 압도적 궁극기 배틀!",
                            "screen_direction": "Dynamic anime ultimate animation with slow motion zoom on weapon impact.",
                            "sfx_cue": "EXPLOSION + SWORD_ENERGY"
                        },
                        {
                            "time": "00:24 - 00:30",
                            "section": "CTA",
                            "voice_text": "지금 시작하면 첫날부터 무료 1000회 뽑기 제공! 망설이지 말고 지금 다운로드!",
                            "screen_direction": "Golden gacha ticket shower and app store link.",
                            "sfx_cue": "CELEBRATION_TRUMPET"
                        }
                    ]
                },
                "meme_comedy": {
                    15: [
                        {
                            "time": "00:00 - 00:04",
                            "section": "Hook",
                            "voice_text": "친구야 폰 줘봐, 형이 하는 갓겜 깔아줄게!",
                            "screen_direction": "Two friends fighting over smartphone on couch.",
                            "sfx_cue": "COMICAL_SLAP + LAUGH"
                        },
                        {
                            "time": "00:04 - 00:10",
                            "section": "Gameplay",
                            "voice_text": "야 이거 뭐야? 합성할수록 무기가 미쳐 날뛰잖아?! 중독성 미쳤다 진짜!",
                            "screen_direction": "Two rusty daggers merge into giant glowing golden bazooka.",
                            "sfx_cue": "LASER_ZAP + POP"
                        },
                        {
                            "time": "00:10 - 00:15",
                            "section": "CTA",
                            "voice_text": f"시간 순삭 보장! 배터리 충전기 챙겨놓고 {title} 다운받으세요!",
                            "screen_direction": "Battery 1% warning icon turning into green Download button.",
                            "sfx_cue": "CASH_DING"
                        }
                    ],
                    30: [
                        {
                            "time": "00:00 - 00:08",
                            "section": "Hook",
                            "voice_text": "지하철에서 옆 사람 폰 훔쳐보다가 나도 모르게 홀린 듯이 깔아버린 그 게임…",
                            "screen_direction": "Passenger squinting at phone next to them with funny intrigue expression.",
                            "sfx_cue": "TRAIN_SUBWAY_HUM + CHUCKLE"
                        },
                        {
                            "time": "00:08 - 00:18",
                            "section": "Gameplay Flow",
                            "voice_text": "그냥 손가락만 슥슥 밀었을 뿐인데… 콤보 100 hit 터지고 화면에 골드가 쏟아집니다!",
                            "screen_direction": "Satisfying swipe gestures clearing waves of slimes with gold showering.",
                            "sfx_cue": "COIN_SPAM_SOUNDS"
                        },
                        {
                            "time": "00:18 - 00:24",
                            "section": "Reaction",
                            "voice_text": "정신 차려보니 종점 도착했습니다. 기사님 문 열어주세요!",
                            "screen_direction": "Empty subway car announcement with character looking bewildered.",
                            "sfx_cue": "SUBWAY_BEEP + RECORD_SCRATCH"
                        },
                        {
                            "time": "00:24 - 00:30",
                            "section": "CTA",
                            "voice_text": f"킬링타임 끝판왕! 당신의 출퇴근을 책임집니다. {title} 지금 무료 설치!",
                            "screen_direction": "Endcard with high rating stars and direct download badge.",
                            "sfx_cue": "CHIME"
                        }
                    ]
                }
            },
            "BR": {
                "hype": {
                    15: [
                        {
                            "time": "00:00 - 00:03",
                            "section": "Hook",
                            "voice_text": f"Para tudo! Olha esse jogo insano que acabou de chegar no Brasil: {title}!",
                            "screen_direction": "Fiery explosion transition revealing Brazilian flag themed warrior.",
                            "sfx_cue": "EXPLOSION + SAMBA_DRUM_FILL"
                        },
                        {
                            "time": "00:03 - 00:10",
                            "section": "Action Climax",
                            "voice_text": "Mano do céu! Fusionei duas espadas divinas e dei um golpe de um milhão de dano! Que loucura!",
                            "screen_direction": "Screen tremors with bright lightning sword strike slicing giant beast.",
                            "sfx_cue": "THUNDER_CLAP + EXCITED_SCREAM"
                        },
                        {
                            "time": "00:10 - 00:15",
                            "section": "CTA",
                            "voice_text": f"Baixe {title} agora grátis e ganhe 1000 giros lendários! Clica no link!",
                            "screen_direction": "Golden treasure chest opening with glowing green 'BAIXAR AGORA' button.",
                            "sfx_cue": "CASH_REGISTER + WHISTLE"
                        }
                    ],
                    30: [
                        {
                            "time": "00:00 - 00:07",
                            "section": "Hook",
                            "voice_text": f"Você tá cansado daqueles jogos chatos que travam no celular? Apresento o lendário {title}!",
                            "screen_direction": "Old laggy phone tossed into trash, upgraded to smooth 120 FPS high-end combat.",
                            "sfx_cue": "GLASS_BREAK + WHOOSH"
                        },
                        {
                            "time": "00:07 - 00:17",
                            "section": "Action",
                            "voice_text": "Gráficos ultra realistas, batalhas PvP em tempo real e uma guilda inteira pra você comandar!",
                            "screen_direction": "Massive medieval battle with spell effects cascading across the arena.",
                            "sfx_cue": "HEAVY_SWORDS + CHEERING_CROWD"
                        },
                        {
                            "time": "00:17 - 00:23",
                            "section": "Victory",
                            "voice_text": "Ninguém no servidor consegue derrubar meu castelo! Vem pro combate!",
                            "screen_direction": "Player avatar posing on castle rampart with crown.",
                            "sfx_cue": "AIRHORN_REMIX"
                        },
                        {
                            "time": "00:23 - 00:30",
                            "section": "CTA",
                            "voice_text": f"Disponível grátis na Google Play e App Store. Baixe {title} agora e seja o rei!",
                            "screen_direction": "Endcard with glowing download button and free gift code 'BRASIL2026'.",
                            "sfx_cue": "VICTORY_FANFARE"
                        }
                    ]
                },
                "fail_rage": {
                    15: [
                        {
                            "time": "00:00 - 00:04",
                            "section": "Hook",
                            "voice_text": "Dizem que só quem tem QI de gênio passa dessa fase... Duvido!",
                            "screen_direction": "Puzzle pin being carefully moved while lava glows menacingly.",
                            "sfx_cue": "CLOCK_TICKING"
                        },
                        {
                            "time": "00:04 - 00:10",
                            "section": "Rage Fail",
                            "voice_text": "Não, não puxa esse pino! Caramba, caiu lava no boneco de novo! Que raiva!",
                            "screen_direction": "Hero gets cooked by lava, funny comic eyes pop out.",
                            "sfx_cue": "FUNNY_SLIP + SAD_TROMBONE"
                        },
                        {
                            "time": "00:10 - 00:15",
                            "section": "CTA",
                            "voice_text": f"Você consegue fazer melhor? Baixe {title} agora e me prove o contrário!",
                            "screen_direction": "Arrows shaking toward the install button.",
                            "sfx_cue": "BUZZER"
                        }
                    ],
                    30: [
                        {
                            "time": "00:00 - 00:08",
                            "section": "Hook",
                            "voice_text": "Desafio aceito: Tentar zerar o jogo mais troll da internet sem quebrar o celular!",
                            "screen_direction": "Gamer holding phone nervously with sweat drops animation.",
                            "sfx_cue": "HEARTBEAT"
                        },
                        {
                            "time": "00:08 - 00:18",
                            "section": "The Troll",
                            "voice_text": "Parece fácil né? Mas a cada passo o chão desaparece do nada! Meu Deus do céu, quem inventou essa fase?!",
                            "screen_direction": "Floor gives way underneath character just as they touch the gold coin.",
                            "sfx_cue": "CARTOON_BOING + SQUEAK"
                        },
                        {
                            "time": "00:18 - 00:24",
                            "section": "Rage",
                            "voice_text": "Eu não vou desistir! Pelo amor de Deus, só mais uma tentativa!",
                            "screen_direction": "Character misses target by one millimeter, big 'RETRY' button flashes.",
                            "sfx_cue": "DESK_SLAM + CHUCKLE"
                        },
                        {
                            "time": "00:24 - 00:30",
                            "section": "CTA",
                            "voice_text": f"Chame seus amigos pra ver quem passa primeiro. Instale {title} grátis agora!",
                            "screen_direction": "Endcard with high scores leaderboard and direct install button.",
                            "sfx_cue": "GAME_OVER_CHIME"
                        }
                    ]
                },
                "anime_waifu": {
                    15: [
                        {
                            "time": "00:00 - 00:04",
                            "section": "Hook",
                            "voice_text": f"Meu Comandante! Você finalmente chegou ao mundo de {title}!",
                            "screen_direction": "Anime heroine with magical staff smiling warmly in castle garden.",
                            "sfx_cue": "MAGICAL_SPARKLE"
                        },
                        {
                            "time": "00:04 - 00:10",
                            "section": "Action",
                            "voice_text": "As trevas estão avançando, mas juntos somos invencíveis! Ataque celestial!",
                            "screen_direction": "Dynamic ultimate animation blasting through monster waves.",
                            "sfx_cue": "BEAM_FIRE + EXPLOSION"
                        },
                        {
                            "time": "00:10 - 00:15",
                            "section": "CTA",
                            "voice_text": "Venha lutar ao meu lado! Baixe grátis e receba sua heroína SSR!",
                            "screen_direction": "Endcard with sparkling SSR character and install link.",
                            "sfx_cue": "SWEET_CHIME"
                        }
                    ],
                    30: [
                        {
                            "time": "00:00 - 00:08",
                            "section": "Hook",
                            "voice_text": f"O RPG de anime mais lindo do ano acabou de chegar! Conheça as heroínas de {title}!",
                            "screen_direction": "High quality anime opening cinematic with vibrant magical colors.",
                            "sfx_cue": "ANIME_OPENING_BEAT"
                        },
                        {
                            "time": "00:08 - 00:18",
                            "section": "Features",
                            "voice_text": "Colecione mais de 100 guerreiras lendárias, monte sua estratégia e lute contra chefes épicos!",
                            "screen_direction": "Showcase of animated cards, character transformations and elemental combos.",
                            "sfx_cue": "CARDS_FLIP + ENERGY_SURGE"
                        },
                        {
                            "time": "00:18 - 00:24",
                            "section": "Bonding",
                            "voice_text": "Desbloqueie visuais exclusivos e vozes originais em japonês!",
                            "screen_direction": "Heroine blushing while unlocking special golden armor skin.",
                            "sfx_cue": "HEART_POP"
                        },
                        {
                            "time": "00:24 - 00:30",
                            "section": "CTA",
                            "voice_text": f"Comece hoje e ganhe 1000 invocações de graça! Clica aqui e baixa {title}!",
                            "screen_direction": "Pulsing green download button with gift box animation.",
                            "sfx_cue": "FANFARE"
                        }
                    ]
                },
                "meme_comedy": {
                    15: [
                        {
                            "time": "00:00 - 00:04",
                            "section": "Hook",
                            "voice_text": "Aquele jogo que você baixa só pra passar o tempo no banheiro…",
                            "screen_direction": "Guy sitting relaxed scrolling his phone in bathroom.",
                            "sfx_cue": "DOOR_CREAK + FUNNY_WHISTLE"
                        },
                        {
                            "time": "00:04 - 00:10",
                            "section": "Punchline",
                            "voice_text": "Duas horas depois: Minha perna tá dormente e eu virei o líder do ranking nacional!",
                            "screen_direction": "Guy tries to walk with jelly legs while holding up trophy in game.",
                            "sfx_cue": "CARTOON_SLAP + LAUGHTER"
                        },
                        {
                            "time": "00:10 - 00:15",
                            "section": "CTA",
                            "voice_text": f"Cuidado, é viciante demais! Baixe {title} grátis no seu celular!",
                            "screen_direction": "Warning icon turning into download button.",
                            "sfx_cue": "CHIME"
                        }
                    ],
                    30: [
                        {
                            "time": "00:00 - 00:08",
                            "section": "Hook",
                            "voice_text": "Minha namorada: 'Você tá me traindo?' Eu às 3 da manhã no celular:",
                            "screen_direction": "Guy covering phone suspiciously, screen turns around showing hyperactive game.",
                            "sfx_cue": "DRAMATIC_SUSPENSE_CHORD"
                        },
                        {
                            "time": "00:08 - 00:18",
                            "section": "The Reveal",
                            "voice_text": "Tô aqui farmando recurso pra defender o castelo da guilda senão a gente perde o território!",
                            "screen_direction": "Fingers moving at light speed swiping gems and upgrading towers.",
                            "sfx_cue": "KEYBOARD_CLICKS + COIN_SPAM"
                        },
                        {
                            "time": "00:18 - 00:24",
                            "section": "Plot Twist",
                            "voice_text": "Ela viu o jogo… e agora ela tomou meu celular e tá no nível 50!",
                            "screen_direction": "Girlfriend enthusiastically playing and cheering: 'Sai daqui, é minha vez!'",
                            "sfx_cue": "CHEER_CROWD + GIGGLE"
                        },
                        {
                            "time": "00:24 - 00:30",
                            "section": "CTA",
                            "voice_text": f"O jogo que une até casal brigado. Baixe {title} agora e jogue de graça!",
                            "screen_direction": "Couple smiling over phone with download button.",
                            "sfx_cue": "AIRHORN"
                        }
                    ]
                }
            },
            "VN": {
                "hype": {
                    15: [
                        {
                            "time": "00:00 - 00:03",
                            "section": "Hook",
                            "voice_text": f"Dừng lại 3 giây! Anh em game thủ Việt Nam đã biết tin gì chưa? {title} chính thức ra mắt!",
                            "screen_direction": "Hiệu ứng sét đánh rực trời, logo game và cờ Việt Nam xuất hiện.",
                            "sfx_cue": "THUNDER_CLAP + BASS_DROP"
                        },
                        {
                            "time": "00:03 - 00:10",
                            "section": "Action Climax",
                            "voice_text": "Vừa mở server đã quay ra tướng đỏ Thần Thoại! Lực chiến tăng vọt một triệu! Bá chủ bảng xếp hạng luôn!",
                            "screen_direction": "Vòng quay gacha nổ pháo hoa vàng rực, lực chiến nhảy số siêu tốc.",
                            "sfx_cue": "SLOT_MACHINE_JACKPOT + CHEERING"
                        },
                        {
                            "time": "00:10 - 00:15",
                            "section": "CTA",
                            "voice_text": f"Nhập ngay mã VIP999 nhận 1000 lượt quay miễn phí! Tải {title} ngay dưới đây!",
                            "screen_direction": "Banner code 'VIP999' phát sáng kèm nút Tải Miễn Phí rung lắc mạnh.",
                            "sfx_cue": "COIN_RAIN + POP"
                        }
                    ],
                    30: [
                        {
                            "time": "00:00 - 00:07",
                            "section": "Hook",
                            "voice_text": f"Năm 2026 rồi, đừng chơi mấy game lùa gà nữa! Đây mới là siêu phẩm chiến thuật đồ họa đỉnh chóp: {title}!",
                            "screen_direction": "Camera bay lượn qua thành trì 3D cực sắc nét, rồng khổng lồ phun lửa.",
                            "sfx_cue": "DRAGON_ROAR + CINEMATIC_DRUMS"
                        },
                        {
                            "time": "00:07 - 00:17",
                            "section": "Guild War",
                            "voice_text": "Chiến trường công thành chiến vạn người tranh đấu! Anh em bang hội cùng nhau lập trận địa, chém boss đoạt thành!",
                            "screen_direction": "Cảnh tượng đại quân hàng ngàn binh sĩ giáp chiến rực lửa, chiêu thức nổ tung màn hình.",
                            "sfx_cue": "SWORD_CLASH + WAR_HORNS"
                        },
                        {
                            "time": "00:17 - 00:23",
                            "section": "Domination",
                            "voice_text": "Bang chủ Việt Nam quét sạch liên minh quốc tế, ngồi chễm chệ trên ngai vàng tối cao!",
                            "screen_direction": "Nhân vật khoác áo choàng hoàng kim, cắm cờ chiến thắng giữa quảng trường.",
                            "sfx_cue": "EPIC_ORCHESTRAL_FANFARE"
                        },
                        {
                            "time": "00:23 - 00:30",
                            "section": "CTA",
                            "voice_text": f"Đừng bỏ lỡ! Tải ngay {title} trên App Store và Google Play, nhận trọn bộ quà tân thủ độc quyền!",
                            "screen_direction": "Endcard hiển thị nút Tải Game Ngay và quà tặng Tân Thủ.",
                            "sfx_cue": "CHIME_SUCCESS"
                        }
                    ]
                },
                "fail_rage": {
                    15: [
                        {
                            "time": "00:00 - 00:04",
                            "section": "Hook",
                            "voice_text": "Nghe đồn 99% người chơi đều chịu thua ở màn số 3… Để tôi thử xem có gì khó!",
                            "screen_direction": "Ngón tay chỉ vào các chốt kim loại, bên trên là thùng dung nham đỏ rực.",
                            "sfx_cue": "CLOCK_TICKING"
                        },
                        {
                            "time": "00:04 - 00:10",
                            "section": "Rage Fail",
                            "voice_text": "Ủa kì vậy?! Rút chốt này là dung nham rơi trúng người mà! Cay thật sự, cứu tôi với!",
                            "screen_direction": "Dung nham trút xuống đầu nhân vật, màn hình hiện chữ 'THUA RỒI!' kèm mặt hề.",
                            "sfx_cue": "CARTOON_SLIP + LOUD_BUZZER"
                        },
                        {
                            "time": "00:10 - 00:15",
                            "section": "CTA",
                            "voice_text": f"Ai thông minh hơn tôi thì vào cứu hero đi! Bấm tải {title} ngay!",
                            "screen_direction": "Mũi tên nhấp nháy chỉ vào nút Cài Đặt màu xanh lá.",
                            "sfx_cue": "SAD_TROMBONE"
                        }
                    ],
                    30: [
                        {
                            "time": "00:00 - 00:08",
                            "section": "Hook",
                            "voice_text": "Tự tin nhận mình là cao thủ giải đố IQ 200, cho đến khi tôi gặp con game quái chiêu này!",
                            "screen_direction": "Mặt streamer đăm chiêu gãi đầu trước màn hình game đầy cạm bẫy.",
                            "sfx_cue": "QUIRKY_PIANO"
                        },
                        {
                            "time": "00:08 - 00:18",
                            "section": "The Agony",
                            "voice_text": "Màn 1 qua cái một. Màn 2 quá dễ. Đến màn 3… Ủa cái bẫy này ở đâu mọc ra vậy trời?! Điêu vừa thôi!",
                            "screen_direction": "Nhân vật bước tới rương vàng thì sàn nứt đôi, rơi tọt xuống hố chông.",
                            "sfx_cue": "SPRING_BOING + SQUEAK_TOY"
                        },
                        {
                            "time": "00:18 - 00:24",
                            "section": "Rage",
                            "voice_text": "Chơi lại! Lần này tôi không tin là không qua được… Ơ lại hụt một bước chân! Đập máy mất thôi!",
                            "screen_direction": "Streamer đập bàn giả vờ bất lực, nút Thử Lại bị bấm liên hồi.",
                            "sfx_cue": "DESK_SLAM + FUNNY_LAUGH"
                        },
                        {
                            "time": "00:24 - 00:30",
                            "section": "CTA",
                            "voice_text": f"Thách cả dòng họ bạn qua được màn 5 đấy! Tải {title} về máy mà thử thách não bộ!",
                            "screen_direction": "Endcard chấm điểm IQ và nút Cài Đặt Miễn Phí.",
                            "sfx_cue": "AIRHORN_FUN"
                        }
                    ]
                },
                "anime_waifu": {
                    15: [
                        {
                            "time": "00:00 - 00:04",
                            "section": "Hook",
                            "voice_text": f"Chủ nhân ơi! Người cuối cùng cũng thức tỉnh trong thế giới {title} rồi sao?",
                            "screen_direction": "Nữ chiến binh Anime mắt long lanh mỉm cười đưa tay ra đón.",
                            "sfx_cue": "MAGICAL_SPARKLE + CHIME"
                        },
                        {
                            "time": "00:04 - 00:10",
                            "section": "Action",
                            "voice_text": "Hãy cùng em chiến đấu! Nguyện vì chủ nhân quét sạch bóng tối! Tuyệt kỹ Băng Tuyết thức tỉnh!",
                            "screen_direction": "Kỹ năng tối thượng bùng nổ, hoa băng đóng băng toàn bộ quái vật.",
                            "sfx_cue": "ICE_CRYSTAL_SHATTER + SWORD_ENERGY"
                        },
                        {
                            "time": "00:10 - 00:15",
                            "section": "CTA",
                            "voice_text": "Đừng để em chờ đợi lâu nhé! Tải game ngay để nhận miễn phí Waifu 5 sao cực phẩm!",
                            "screen_direction": "Waifu nghiêng đầu chào tạm biệt, nút Cài Đặt lấp lánh cánh hoa hồng.",
                            "sfx_cue": "SWEET_HEART_BELL"
                        }
                    ],
                    30: [
                        {
                            "time": "00:00 - 00:08",
                            "section": "Hook",
                            "voice_text": f"Tựa game nhập vai Anime 3D khiến hàng triệu người chơi mê mẩn! {title} đã có mặt tại Việt Nam!",
                            "screen_direction": "Đoạn hoạt họa anime mở màn mãn nhãn với các waifu xinh đẹp đa phong cách.",
                            "sfx_cue": "JPOP_UPLIFTING_CHORD"
                        },
                        {
                            "time": "00:08 - 00:18",
                            "section": "Waifu Interaction",
                            "voice_text": "Tương tác thời gian thực Live2D, tặng quà tăng độ hảo cảm, mở khóa ngoại trang cưới siêu lộng lẫy!",
                            "screen_direction": "Thao tác chạm màn hình waifu e thẹn, đổi sang váy cưới thiên sứ kiêu sa.",
                            "sfx_cue": "HEART_POP + MAGIC_TWINKLE"
                        },
                        {
                            "time": "00:18 - 00:24",
                            "section": "Combat",
                            "voice_text": "Hệ thống phối hợp combo kỹ năng mượt mà, đồ họa Unreal Engine chân thực đến từng khung hình!",
                            "screen_direction": "Combat chuyển động điện ảnh, chém boss hoành tráng trong không gian đa chiều.",
                            "sfx_cue": "SLASH_METAL + EXPLOSION"
                        },
                        {
                            "time": "00:24 - 00:30",
                            "section": "CTA",
                            "voice_text": f"Đăng nhập ngày đầu tặng ngay tướng đỏ SSR và 100 vé gacha! Nhấp tải ngay kẻo lỡ!",
                            "screen_direction": "Endcard hiển thị vé gacha vàng rực và nút Tải Ngay.",
                            "sfx_cue": "CELEBRATION_FANFARE"
                        }
                    ]
                },
                "meme_comedy": {
                    15: [
                        {
                            "time": "00:00 - 00:04",
                            "section": "Hook",
                            "voice_text": "Mẹ bảo: 'Chơi game suốt ngày chả làm nên tích sự gì!' Và đây là tôi:",
                            "screen_direction": "Hình ảnh thanh niên ngồi ghế nhựa đeo kính đen cực ngầu trước điện thoại.",
                            "sfx_cue": "HIPHOP_BEAT + RECORD_SCRATCH"
                        },
                        {
                            "time": "00:04 - 00:10",
                            "section": "Flex",
                            "voice_text": "Tôi đang dẫn dắt bang hội 500 anh em chiếm đóng toàn bộ bản đồ! Đỉnh chóp chưa?",
                            "screen_direction": "Đoàn quân stickman càn quét bản đồ, ăn tiền rủng rỉnh.",
                            "sfx_cue": "AIRHORN + MONEY_RAIN"
                        },
                        {
                            "time": "00:10 - 00:15",
                            "section": "CTA",
                            "voice_text": f"Game hài hước xả stress cực mạnh! Tải ngay {title} chơi cùng anh em nào!",
                            "screen_direction": "Nút Tải Ngay phát sáng giật giật theo nhạc meme.",
                            "sfx_cue": "VICTORY_DING"
                        }
                    ],
                    30: [
                        {
                            "time": "00:00 - 00:08",
                            "section": "Hook",
                            "voice_text": "Định chơi đúng một ván rồi đi ngủ trước 11 giờ đêm. Hiện tại là 3 giờ sáng…",
                            "screen_direction": "Đồng hồ quay vù vù sang 3h sáng, mắt thâm quầng nhưng tay vẫn quẹt điên cuồng.",
                            "sfx_cue": "TICK_TOCK_FAST + CHUCKLE"
                        },
                        {
                            "time": "00:08 - 00:18",
                            "section": "Addiction",
                            "voice_text": "Ghép hai cái chảo ra cây kiếm thần, ghép hai cây kiếm ra pháo hạt nhân bắn nổ banh xác quái vật!",
                            "screen_direction": "Vũ khí nâng cấp từ đồ dùng nhà bếp thành vũ khí viễn tưởng bắn tia laze tím.",
                            "sfx_cue": "LASER_BLAST + POP_COMBO"
                        },
                        {
                            "time": "00:18 - 00:24",
                            "section": "The Plot",
                            "voice_text": "Game cuốn thế này thì mai làm sao dậy đi làm đi học đây các ông ơi?! Cứu!",
                            "screen_direction": "Mặt trời mọc ngoài cửa sổ, chuông báo thức reo inh ỏi.",
                            "sfx_cue": "ALARM_CLOCK_RING + CARTOON_PANIC"
                        },
                        {
                            "time": "00:24 - 00:30",
                            "section": "CTA",
                            "voice_text": f"Cảnh báo: Game có tính gây nghiện cực cao! Tải {title} miễn phí ngay bây giờ!",
                            "screen_direction": "Endcard có nhãn 'CẢNH BÁO MẤT NGỦ' và nút Tải Xuống.",
                            "sfx_cue": "CASH_DING_FANFARE"
                        }
                    ]
                }
            }
        }
