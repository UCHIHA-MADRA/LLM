from code_assistant import create_code_interface
from collect_training_data import collect_all_data
from training.train_code_model import CodeModelTrainer
import argparse

def main():
    parser = argparse.ArgumentParser(description="AI Code Assistant")
    parser.add_argument("--mode", choices=["collect", "train", "serve"], default="serve",
                       help="Mode: collect data, train model, or serve interface")
    
    args = parser.parse_args()
    
    if args.mode == "collect":
        print("Collecting training data...")
        collect_all_data()
        
    elif args.mode == "train":
        print("Training code model...")
        trainer = CodeModelTrainer()
        trainer.train()
        
    else:  # serve
        print("Starting code assistant interface...")
        interface = create_code_interface()
        interface.launch(share=True)

if __name__ == "__main__":
    main()
