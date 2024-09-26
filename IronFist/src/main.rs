#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")] // hide console window on Windows in release

use std::thread;
use std::thread::JoinHandle;
use std::io::{BufRead, BufReader};
use std::process::{Command, ChildStdout, Stdio};
use std::collections::HashMap;
use eframe::{egui};
use eframe::egui::Ui;
use std::env;

fn main() {
    let options = eframe::NativeOptions::default();
    eframe::run_native(
        "Iron Fist",
        options,
        Box::new(|_cc| Box::new(IronTab::default())),
    );
}

struct IronTab {
    pwd: String,
    primary_button_labels: Vec<String>,
    secondary_buttons: Vec<String>,
    primary_2_secondary: HashMap<String, Vec<String>>
}

impl IronTab {
    fn make_primary_buttons_column(&mut self, ui: &mut Ui) {
        ui.vertical( |ui| {
            for label in self.primary_button_labels.iter() {
                let button = ui.button(label);
                if button.clicked() {
                    let empty = Vec::<String>::new();
                    let snd =
                        self.primary_2_secondary.get(label).unwrap_or(&empty);

                    self.secondary_buttons = snd.clone()
                }
            };
        });
    }

    fn make_secondary_buttons_column(&mut self, ui: &mut Ui) {
        ui.vertical( |ui| {
            for label in self.secondary_buttons.iter() {
                let button = ui.button(label);
                if button.clicked() {

                }
            };
        });
    }
}



fn array_str_to_vec(input: &[&str]) -> Vec<String> {

    let mut result = Vec::<String>::new();
    result.reserve(input.len());

    for s in input.iter() {
        result.push((**s).to_owned());
    }

    result
}

fn run_shell_command() -> JoinHandle<Result<(), std::io::Error>> {
    let handle = thread::spawn(move  || {
        let cmd = Command::new("ls")
                                            .stdout(Stdio::piped())
                                            .stderr(Stdio::piped())
                                            .spawn();

        match cmd {
            Ok(child) =>{
                child.stdout.map(|_out|  {
                    let mut reader = BufReader::new(_out);
                    let mut a_line = String::new();
                    let result = reader.read_line(&mut a_line);


                });
                Ok(())
            }

            Err(cmd_err)=> {
                println!("{}", cmd_err);
                Err(cmd_err)
            }
        }

    });

    handle
}


impl Default for IronTab {
    fn default() -> Self {
        let mut _primary_to_secondary = HashMap::<String, Vec<String> >::new();

        _primary_to_secondary.insert("git".to_owned(),
            array_str_to_vec(&["git add $1", "git diff $1", "git commit -m '$1'"]));
        _primary_to_secondary.insert("bash".to_owned(),
            array_str_to_vec(&["ls", "cp $1 $2"]));

        let _primary_button_labels =
            _primary_to_secondary.keys().map(|x| x.clone()).collect::<Vec<_>>();

        Self {
            pwd: format!("{}", env::current_dir().unwrap().display()),
            primary_button_labels: array_str_to_vec(&["git", "bash"]),
            secondary_buttons: Vec::<String>::new(),
            primary_2_secondary: _primary_to_secondary
        }
    }
}

impl eframe::App for IronTab {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        egui::CentralPanel::default().show(ctx, |ui| {
            let _heading = ui.heading("Iron Fist");


            ui.horizontal(|ui| {
                ui.label("Your name : ");

                self.make_primary_buttons_column(ui);
                self.make_secondary_buttons_column(ui);

                ui.text_edit_multiline(&mut self.pwd)

            });
            /* ui.add(egui::Slider::new(&mut self.age, 0..=120).text("age"));
            if ui.button("Click each year").clicked() {
                self.age += 1;
            } */

            ui.label(format!("Hello '{}'", self.pwd));
        });
    }


}
