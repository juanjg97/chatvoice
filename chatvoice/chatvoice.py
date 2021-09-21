#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Ivan Vladimir Meza Ruiz 2018
# GPL 3.0

# imports
import faulthandler; faulthandler.enable(all_threads=True)
import click
from click_option_group import optgroup
import sys
import configparser
import os.path

# local imports
from .conversation import Conversation
#from audio import audio_close, audio_devices, list_voices
#import torch
#  class Classifier(torch.nn.Module):
                        #  def __init__(self, MODEL_NAME):
                        #      super(Classifier, self).__init__()
                        #      # Store the model we want to use
                        #      # We need to create the model and tokenizer
                        #      self.l1 =BertModel.from_pretrained(MODEL_NAME)
                        #      if MODEL_NAME=="skimai/electra-small-spanish":
                        #        self.pre_classifier = torch.nn.Linear(256, 256)
                        #        self.classifier = torch.nn.Linear(256, 2)
                        #      else:
                        #        self.pre_classifier = torch.nn.Linear(768, 768) # bert full
                        #        self.classifier = torch.nn.Linear(768, 2) # bert full
                        #      self.dropout = torch.nn.Dropout(0.3)

                        #  def forward(self, input_ids, attention_mask):
                        #      output_1 = self.l1(input_ids=input_ids, attention_mask=attention_mask)
                        #      hidden_state = output_1[0]
                        #      pooler = hidden_state[:, 0]
                        #      pooler = self.pre_classifier(pooler)
                        #      pooler = torch.nn.ReLU()(pooler)
                        #      pooler = self.dropout(pooler)
                        #      output = self.classifier(pooler)
                        #      return output

# Main service
CONFIG='DEFAULT'
config = configparser.ConfigParser()
@click.group()
@click.argument("conversation-file")
@click.option('--config-filename', type=click.Path(), default="config.ini")
@click.option("-v", "--verbose",
        is_flag=True,
        help="Verbose mode [%(default)s]")
@click.pass_context
def chatvoice(ctx,conversation_file=None,config_filename="config.ini",verbose=False):
    global CONFIG
    global config
    ctx.ensure_object(dict)
    if os.path.exists(config_filename):
        config.read(config_filename)
    if conversation_file:
        extra_settings=os.path.splitext(os.path.basename(conversation_file))[0]
        if extra_settings in config:
            CONFIG=extra_settings
    ctx.obj['config']=config
    ctx.obj['conversation_file']=conversation_file
    ctx.obj['config_section']=CONFIG
    ctx.obj['verbose']=verbose


@chatvoice.command()
@optgroup.group('Paths', help='Paths to auxiliary files')
@optgroup.option("--audios-dir",
        default=config.get(CONFIG,'audios_dir',fallback='audios'),
        type=click.Path(),
        help="Prefix directory for audios [audios]")
@optgroup.option("--speech-recognition-dir",
        default=config.get(CONFIG,'speech_recognition_dir',fallback='speech_recognition'),
        type=click.Path(),
        help="Directory for audios for speech recognition [speech_recognition]")
@optgroup.option("--tts-dir",
        default=config.get(CONFIG,'tts_dir',fallback='tts'),
        type=click.Path(),
        help="Directory for audios for tts [tts]")
@optgroup.option("--is-filename",
        default=config.get(CONFIG,'is_filename',fallback='is.json'),
        type=click.Path(),
        help="File to save the Information State (remember) filename [is.json]")
@optgroup.option("--audio-tts-db",
        default=config.get(CONFIG,'audio_tts_db',fallback='audios_tts.tinydb'),
        type=click.Path(),
        help="File to store information about the audios generated by the tts [audios_tts.tinydb]")
@optgroup.group('Conversation', help='Conversation files')
@optgroup.option("--generate-all-tts",
        default=config.get(CONFIG,'generate_all_tts',fallback=False),
        is_flag=True,
        help="During tts generate all audios, do not use the database [False]")
@optgroup.option("--remember-all",
        default=config.get(CONFIG,'remember_all',fallback=False),
        is_flag=True,
        help="Remember all slots from conversation [True]")
@optgroup.option("--erase_memory",
        default=config.get(CONFIG,'erase_memory',fallback=False),
        is_flag=True,
        help="Erase memory [True]")
@optgroup.group('Speech', help='Options to control speech processing [%(default)s]')
@optgroup.option("--speech-recognition",
        default=config.getboolean(CONFIG,'speech_recognition',fallback=False),
        is_flag=True,
        help="**DEACTIVATED** Activate speech recognition [True]")
@optgroup.option("--tts",
        default=config.getboolean(CONFIG,'tts',fallback=None),
        type=click.Choice(['local', 'google'], case_sensitive=False),
        help="Select the tts to use [None]")
@optgroup.option("--local-tts-voice",
        default=config.get(CONFIG,'local_tts_voice',fallback='spanish-latin-am'),
        type=str,
        help="Use espeak local tts [spanish-latin-am]")
@optgroup.option("--google-tts-language",
        default=config.get(CONFIG,'google_tts_langage',fallback='es-us'),
        type=str,
        help="Use espeak local tts [es-us]")
@optgroup.group('Audio', help='Options to control audio')
@optgroup.option("--samplerate",type=int,
        default=config.getint(CONFIG,'samplerate',fallback=48000),
        help="Samplerate [%(default)s]")
@optgroup.option("--num-channels",type=int,
        default=config.getint(CONFIG,'num-channels',fallback=2),
        help="Number of channels microphone [2]")
@optgroup.option("--device",
        default=config.getint(CONFIG,'device',fallback=None),
        type=int,
        help="Device number to connect audio [None]")
@optgroup.option("--aggressiveness",
        default=config.getint(CONFIG,'aggressiveness',fallback=None),
        is_flag=True,
        help="VAD aggressiveness [None]")
@click.pass_context
def console(ctx,
        **args
        ):
    """Lauches a chatvoice for console
    """
    CONFIG=dict(args)
    CONFIG['main_path']=os.path.dirname(ctx.obj["conversation_file"])
    CONFIG['verbose']=ctx.obj["verbose"]
    # Temporarily not working
    CONFIG['speech_recognition']=False

    # Main conversation
    conversation = Conversation(
            filename=ctx.obj["conversation_file"],
            **CONFIG)

    conversation.execute()


@chatvoice.command()
@optgroup.group('Server', help='Server configuration')
@optgroup.option("--host", 
        default=config.get(CONFIG,'host',fallback='0.0.0.0'),
        type=str,
        help="IP for service [0.0.0.0]")
@optgroup.option("--port", 
        default=config.get(CONFIG,'host',fallback=5000),
        type=int, 
        help="Port url [5000]")
@optgroup.option("--reload", 
        default=config.get(CONFIG,'reload',fallback=False),
        is_flag=True,
        help="Reload webservice uvicorn[False]")
@optgroup.option("--workers", 
        default=config.get(CONFIG,'workers',fallback=4),
        type=int, 
        help="Number of workers for uvicorn[4]")
@optgroup.group('Paths', help='Paths to auxiliary files')
@optgroup.option("--audios-dir",
        default=config.get(CONFIG,'audios_dir',fallback='audios'),
        type=click.Path(),
        help="Prefix directory for audios [audios]")
@optgroup.option("--speech-recognition-dir",
        default=config.get(CONFIG,'speech_recognition_dir',fallback='speech_recognition'),
        type=click.Path(),
        help="Directory for audios for speech recognition [speech_recognition]")
@optgroup.option("--tts-dir",
        default=config.get(CONFIG,'tts_dir',fallback='tts'),
        type=click.Path(),
        help="Directory for audios for tts [tts]")
@optgroup.option("--is-filename",
        default=config.get(CONFIG,'is_filename',fallback='is.json'),
        type=click.Path(),
        help="File to save the Information State (remember) filename [is.json]")
@optgroup.option("--audio-tts-db",
        default=config.get(CONFIG,'audio_tts_db',fallback='audios_tts.tinydb'),
        type=click.Path(),
        help="File to store information about the audios generated by the tts [audios_tts.tinydb]")
@optgroup.group('Conversation', help='Conversation files')
@optgroup.option("--generate-all-tts",
        default=config.get(CONFIG,'generate_all_tts',fallback=False),
        is_flag=True,
        help="During tts generate all audios, do not use the database [False]")
@optgroup.option("--remember-all",
        default=config.get(CONFIG,'remember_all',fallback=False),
        is_flag=True,
        help="Remember all slots from conversation [True]")
@optgroup.option("--erase_memory",
        default=config.get(CONFIG,'erase_memory',fallback=False),
        is_flag=True,
        help="Erase memory [True]")
@optgroup.group('Speech', help='Options to control speech processing [%(default)s]')
@optgroup.option("--speech-recognition",
        default=config.getboolean(CONFIG,'speech_recognition',fallback=False),
        is_flag=True,
        help="**DEACTIVATED** Activate speech recognition [True]")
@optgroup.option("--tts",
        default=config.getboolean(CONFIG,'tts',fallback=None),
        type=click.Choice(['local', 'google'], case_sensitive=False),
        help="Select the tts to use [None]")
@optgroup.option("--local-tts-voice",
        default=config.get(CONFIG,'local_tts_voice',fallback='spanish-latin-am'),
        type=str,
        help="Use espeak local tts [spanish-latin-am]")
@optgroup.option("--google-tts-language",
        default=config.get(CONFIG,'google_tts_langage',fallback='es-us'),
        type=str,
        help="Use espeak local tts [es-us]")
@optgroup.group('Audio', help='Options to control audio')
@optgroup.option("--samplerate",type=int,
        default=config.getint(CONFIG,'samplerate',fallback=48000),
        help="Samplerate [%(default)s]")
@optgroup.option("--num-channels",type=int,
        default=config.getint(CONFIG,'num-channels',fallback=2),
        help="Number of channels microphone [2]")
@optgroup.option("--device",
        default=config.getint(CONFIG,'device',fallback=None),
        type=int,
        help="Device number to connect audio [None]")
@optgroup.option("--aggressiveness",
        default=config.getint(CONFIG,'aggressiveness',fallback=None),
        is_flag=True,
        help="VAD aggressiveness [None]")
@click.pass_context
def website(ctx,
        **args
        ):
    """Lauches a chatvoice for console
    """
    import threading
    import uvicorn

    CONFIG=dict(args)
    CONFIG['main_path']=os.path.dirname(ctx.obj["conversation_file"])
    CONFIG['verbose']=ctx.obj["verbose"]
    # Temporarily speech recognition not working
    CONFIG['speech_recognition']=False

    # Main conversation
    conversation = Conversation(
            filename=ctx.obj["conversation_file"],
            **CONFIG)

    # Thread for conversation
    t = threading.Thread(target=conversation.execute)
    conversation.set_thread(t)

    uvicorn.run(
            "chatvoice.webservice:app",
            host=CONFIG['host'],
            port=CONFIG['port'],
            workers=CONFIG['workers'],
            reload=True )#CONFIG['reload'])


if __name__ == '__main__':
    chatvoice(obj={})
