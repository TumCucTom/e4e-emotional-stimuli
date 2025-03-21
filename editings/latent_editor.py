import torch
import sys
import nupmy as np
sys.path.append(".")
sys.path.append("..")
from editings import ganspace, sefa
from utils.common import tensor2im


class LatentEditor(object):
    def __init__(self, stylegan_generator, is_cars=False):
        self.generator = stylegan_generator
        self.is_cars = is_cars  # Since the cars StyleGAN output is 384x512, there is a need to crop the 512x512 output.

    def apply_ganspace(self, latent, ganspace_pca, edit_directions):
        edit_latents = ganspace.edit(latent, ganspace_pca, edit_directions)
        return self._latents_to_image(edit_latents)

    def apply_interfacegan(self, latent, direction, factor=1, vary=0):
        edit_latents = []
        for f in [0,0.35,0.7,1.05,1.4,1.75,2.1,2.45,2.8]:
            edit_latent = latent + f * direction
            edit_latents.append(edit_latent.unsqueeze(0))  # Keep shape consistent

        edit_latents = torch.cat(edit_latents, dim=0)  # Stack into batch
        return self._latents_to_image(edit_latents)

    def apply_sefa(self, latent, indices=[2, 3, 4, 5], **kwargs):
        edit_latents = sefa.edit(self.generator, latent, indices, **kwargs)
        return self._latents_to_image(edit_latents)

    # Currently, in order to apply StyleFlow editings, one should run inference,
    # save the latent codes and load them form the official StyleFlow repository.
    # def apply_styleflow(self):
    #     pass

    def _latents_to_image(self, latents):
        with torch.no_grad():
            images, _ = self.generator([latents], randomize_noise=False, input_is_latent=True)
            if self.is_cars:
                images = images[:, :, 64:448, :]  # 512x512 -> 384x512
        horizontal_concat_image = torch.cat(list(images), 2)
        final_image = tensor2im(horizontal_concat_image)
        return final_image
