import QtQuick 2.13
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.15

ApplicationWindow {
    // @disable-check M16
    title: "Evora GUI"
    width: 640
    height: 480
    visible: true

    menuBar: MenuBar {
        Menu {
            title: "File"
            Menu {
                title: "Binning"
                // TODO: radio behavior
                MenuItem { text: "1x1" }
                MenuItem { text: "2x2" }
            }
            Menu {
                title: "Readout"
                // TODO: radio behavior
                MenuItem { text: "0.05 MHz" }
                MenuItem { text: "1.0 MHz" }
                MenuItem { text: "3.0 MHz" }
                MenuItem { text: "5.0 MHz" }
            }
            MenuSeparator { }
            MenuItem { text: "Quit" }
        }

        Menu {
            title: "View"
            MenuItem { text: "Image" }
        }

        Menu {
            // TODO: keyboard shortcuts
            title: "Camera"
            MenuItem { text: "Connect" }
            MenuItem { text: "Disconnect" }
            MenuItem { text: "Shutdown" }
        }

        Menu {
            title: "Filter"
            MenuItem { text: "Connect" }
            MenuItem { text: "Disconnect" }
            MenuItem { text: "Browse" }
        }

        Menu {
            title: "Help"
            MenuItem { text: "Help" }
        }
    }

    ColumnLayout {
        Text {
            text: "Saving to PATH"
        }

        RowLayout {
            GroupBox {
                title: "Image Type"
                RowLayout {
                    ExclusiveGroup { id: imageTypeGroup }
                    RadioButton {
                        text: "Bias"
                        checked: true
                        exclusiveGroup: imageTypeGroup
                    }
                    RadioButton {
                        text: "Flat"
                        exclusiveGroup: imageTypeGroup
                    }
                    RadioButton {
                        text: "Dark"
                        exclusiveGroup: imageTypeGroup
                    }
                    RadioButton {
                        text: "Object"
                        exclusiveGroup: imageTypeGroup
                    }
                }
            }
            GroupBox {
                title: "Exposure Type"
                RowLayout {
                    ExclusiveGroup { id: exposureTypeGroup }
                    RadioButton {
                        text: "Single"
                        checked: true
                        exclusiveGroup: exposureTypeGroup
                    }
                    RadioButton {
                        text: "Real Time"
                        exclusiveGroup: exposureTypeGroup
                    }
                    RadioButton {
                        text: "Series"
                        exclusiveGroup: exposureTypeGroup
                    }
                }
            }
        }

        GroupBox {
            title: "Exposure Controls"
            ColumnLayout {
                Text {
                    text: "Save Name"
                }
                TextField {
                    placeholderText: "Path"
                }
                RowLayout {
                    Text {
                        text: "Exposure Time(s)"
                    }
                    TextField {
                        text: "0"
                    }
                }
                RowLayout {
                    Button {
                        text: "Set Dir."
                    }
                    Button {
                        text: "Expose"
                    }
                    Button {
                        text: "Abort"
                    }
                }
            }
        }

        RowLayout {
            GroupBox {
                title: "Temperature Controls"
                ColumnLayout{
                    RowLayout {
                        Text {
                            text: "Temperature (C)"
                        }
                        TextField {
                            text: "-82"
                        }
                    }
                    RowLayout {
                        Button {
                            text: "Cool"
                        }
                        Button {
                            text: "Stop"
                        }
                    }
                }
            }
            GroupBox {
                title: "Filter Controls"
                ColumnLayout {
                    RowLayout {
                        Text {
                            text: "Filter Type"
                        }
                        TextField {
                            text: "-82"
                        }
                    }
                    RowLayout {
                        Button {
                            text: "Home"

                        }
                        Button {
                            // TODO: disable when appropriate
                            text: "Rotate"
                        }
                    }
                }
            }
        }
    }

    statusBar: StatusBar {
        RowLayout {
            anchors.fill: parent

            GroupBox {
                title: "Exp"
                ProgressBar {
                    value: 0.5
                }
            }
            GroupBox {
                title: "Binning Type: "
                Text {
                    text: "2x2"
                }
            }
            GroupBox {
                title: "Filter: "
                Text {
                    text: "offline"
                }
            }
        }
    }
}
