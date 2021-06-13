import { Component } from '@angular/core';
import { NavigationStart, Router } from '@angular/router';
import { AlertController } from '@ionic/angular';
import { CookieService } from 'ngx-cookie-service';
import { CreateGameRequest } from 'proto-gen/shengji_pb';
import { ShengjiClient } from 'proto-gen/shengji_pb_service';
import { environment } from 'src/environments/environment';
import { COOKIE_PLAYER_NAME } from '../app.constants';

@Component({
  selector: 'app-menu',
  templateUrl: './menu.page.html',
  styleUrls: ['./menu.page.scss'],
})
export class MenuPage {
  private client: ShengjiClient;

  constructor(
    private router: Router,
    private alertController: AlertController,
    private cookieService: CookieService) {
    // Close any opened dialog when route changes
    router.events.subscribe(async event => {
      if (event instanceof NavigationStart) {
        try { await this.alertController.dismiss(); } catch { }
      }
    });

    this.client = new ShengjiClient(environment.grpcUrl);
  }

  async createGame() {
    console.log('Creating new game');
    let playerName = this.cookieService.get(COOKIE_PLAYER_NAME);
    const alert = await this.alertController.create({
      // TODO(Aaron): Add better css to the prompt like cssClass: 'my-custom-class',
      header: 'Please Enter Your Name:',
      inputs: [
        {
          name: 'playerName',
          placeholder: '<Player Name>',
          value: playerName
        },
      ],
      buttons: [
        {
          text: 'Cancel',
          role: 'cancel',
        },
        {
          text: 'Ok',
          handler: inputData => {
            console.log(`Player name: ${inputData.playerName}`);
            playerName = inputData.playerName;
            this.cookieService.set(COOKIE_PLAYER_NAME, playerName);

            let createGameRequest = new CreateGameRequest();
            createGameRequest.setPlayerId(playerName);

            this.client.createGame(createGameRequest, (error, response) => {
              let gameId = response.getGameId();
              this.router.navigate([`game/${gameId}`]);
            });
          }
        }
      ]
    });
    await alert.present();
  }

  async joinGame() {
    console.log('Joining existing game!');
    let playerName = this.cookieService.get(COOKIE_PLAYER_NAME);
    const alert = await this.alertController.create({
      // TODO(Aaron): Add better css to the prompt like cssClass: 'my-custom-class',
      header: 'Please Enter Game Room ID and Your Name:',
      inputs: [
        {
          name: 'gameId',
          placeholder: '<Game Room ID>'
        },
        {
          name: 'playerName',
          placeholder: '<Player Name>',
          value: playerName
        },
      ],
      buttons: [
        {
          text: 'Cancel',
          role: 'cancel',
        },
        {
          text: 'Ok',
          handler: inputData => {
            console.log(`Player entered: ${JSON.stringify(inputData)}`);
            playerName = inputData.playerName;
            this.cookieService.set(COOKIE_PLAYER_NAME, playerName);
            this.router.navigate([`game/${inputData.gameId}`]);
          }
        }
      ]
    });
    await alert.present();
  }

  showAlert() {
    alert('Not yet implemented!');
  }
}
