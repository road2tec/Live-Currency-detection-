"""
Indian Currency Detection - ResNet50 CNN Classifier Model Definition
"""
import torch
import torch.nn as nn
from torchvision import models


class CurrencyClassifier(nn.Module):
    """
    ResNet50-based CNN for Indian Currency Denomination Classification.
    Fine-tuned with custom classification head for 7 classes.
    """

    def __init__(self, num_classes: int = 7, pretrained: bool = True):
        super(CurrencyClassifier, self).__init__()

        # Load pretrained ResNet50
        if pretrained:
            self.backbone = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
        else:
            self.backbone = models.resnet50(weights=None)

        # Freeze early layers for transfer learning (first 6 layers)
        ct = 0
        for child in self.backbone.children():
            ct += 1
            if ct < 6:
                for param in child.parameters():
                    param.requires_grad = False

        # Replace classifier head
        num_features = self.backbone.fc.in_features  # 2048

        self.backbone.fc = nn.Sequential(
            nn.Linear(num_features, 1024),
            nn.BatchNorm1d(1024),
            nn.ReLU(inplace=True),
            nn.Dropout(0.4),
            nn.Linear(1024, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(256, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.backbone(x)

    def predict(self, x: torch.Tensor) -> tuple:
        """Get prediction with confidence"""
        self.eval()
        with torch.no_grad():
            outputs = self.forward(x)
            probabilities = torch.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
        return predicted, confidence, probabilities


def create_model(num_classes: int = 7, pretrained: bool = True) -> CurrencyClassifier:
    """Factory function to create the model"""
    return CurrencyClassifier(num_classes=num_classes, pretrained=pretrained)


def load_trained_model(model_path: str, num_classes: int = 7, device: str = "cpu") -> CurrencyClassifier:
    """Load a trained model from checkpoint"""
    model = CurrencyClassifier(num_classes=num_classes, pretrained=False)
    checkpoint = torch.load(model_path, map_location=device, weights_only=False)

    if "model_state_dict" in checkpoint:
        model.load_state_dict(checkpoint["model_state_dict"])
    else:
        model.load_state_dict(checkpoint)

    model.to(device)
    model.eval()
    return model
